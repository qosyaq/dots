import os
import json
from tqdm import tqdm
from multiprocessing.pool import ThreadPool
from ocr.model.inference import inference_with_vllm
from ocr.utils.consts import image_extensions, MIN_PIXELS, MAX_PIXELS
from ocr.utils.image_utils import get_image_by_fitz_doc, fetch_image, smart_resize
from ocr.utils.doc_utils import load_images_from_pdf
from ocr.utils.prompts import dict_promptmode_to_prompt
from ocr.utils.layout_utils import (
    post_process_output,
    pre_process_bboxes,
)
from ocr.utils.format_transformer import layoutjson2md


class DotsOCRParser:

    def __init__(
        self,
        protocol="http",
        ip="localhost",
        port=8000,
        model_name="model",
        temperature=0.1,
        top_p=1.0,
        max_completion_tokens=16384,
        num_thread=1,
        dpi=200,
        min_pixels=None,
        max_pixels=None,
    ):
        self.dpi = dpi
        self.protocol = protocol
        self.ip = ip
        self.port = port
        self.model_name = model_name
        self.temperature = temperature
        self.top_p = top_p
        self.max_completion_tokens = max_completion_tokens
        self.num_thread = num_thread
        self.min_pixels = min_pixels
        self.max_pixels = max_pixels

        assert self.min_pixels is None or self.min_pixels >= MIN_PIXELS
        assert self.max_pixels is None or self.max_pixels <= MAX_PIXELS

    def _inference_with_vllm(self, image, prompt):
        response = inference_with_vllm(
            image,
            prompt,
            model_name=self.model_name,
            protocol=self.protocol,
            ip=self.ip,
            port=self.port,
            temperature=self.temperature,
            top_p=self.top_p,
            max_completion_tokens=self.max_completion_tokens,
        )
        return response

    def get_prompt(
        self,
        prompt_mode,
        bbox=None,
        origin_image=None,
        image=None,
        min_pixels=None,
        max_pixels=None,
    ):
        prompt = dict_promptmode_to_prompt[prompt_mode]
        if prompt_mode == "prompt_grounding_ocr":
            assert bbox is not None
            bboxes = [bbox]
            bbox = pre_process_bboxes(
                origin_image,
                bboxes,
                input_width=image.width,
                input_height=image.height,
                min_pixels=min_pixels,
                max_pixels=max_pixels,
            )[0]
            prompt = prompt + str(bbox)
        return prompt

    def _parse_single_image(
        self,
        origin_image,
        prompt_mode,
        save_name,
        source="image",
        page_idx=0,
        bbox=None,
        fitz_preprocess=False,
    ):
        min_pixels, max_pixels = self.min_pixels, self.max_pixels
        if prompt_mode == "prompt_grounding_ocr":
            min_pixels = min_pixels or MIN_PIXELS
            max_pixels = max_pixels or MAX_PIXELS
        if min_pixels is not None:
            assert min_pixels >= MIN_PIXELS, f"min_pixels should >= {MIN_PIXELS}"
        if max_pixels is not None:
            assert max_pixels <= MAX_PIXELS, f"max_pixels should <= {MAX_PIXELS}"

        if source == "image" and fitz_preprocess:
            image = get_image_by_fitz_doc(origin_image, target_dpi=self.dpi)
            image = fetch_image(image, min_pixels=min_pixels, max_pixels=max_pixels)
        else:
            image = fetch_image(
                origin_image, min_pixels=min_pixels, max_pixels=max_pixels
            )
        input_height, input_width = smart_resize(image.height, image.width)
        prompt = self.get_prompt(
            prompt_mode,
            bbox,
            origin_image,
            image,
            min_pixels=min_pixels,
            max_pixels=max_pixels,
        )
        response = self._inference_with_vllm(image, prompt)
        result = {
            "page_no": page_idx,
            "input_height": input_height,
            "input_width": input_width,
        }
        if source == "pdf":
            save_name = f"{save_name}_page_{page_idx}"

        if prompt_mode in [
            "prompt_layout_all_en",
        ]:
            cells, _ = post_process_output(
                response,
                prompt_mode,
                origin_image,
                image,
                min_pixels=min_pixels,
                max_pixels=max_pixels,
            )
            md_content = layoutjson2md(
                origin_image, cells, text_key="text", no_page_hf=False
            )
            result.update(
                {
                    "text": md_content,
                }
            )

            with open(f"pag_{page_idx}", "w", encoding="utf-8") as md_file:
                md_file.write(md_content)
        else:
            result["text"] = response.strip()
        return result

    def parse_image(
        self,
        input_path,
        filename,
        prompt_mode,
        bbox=None,
        fitz_preprocess=False,
    ):
        origin_image = fetch_image(input_path)
        result = self._parse_single_image(
            origin_image,
            prompt_mode,
            filename,
            source="image",
            bbox=bbox,
            fitz_preprocess=fitz_preprocess,
        )
        result["file_path"] = input_path
        return [result]

    def parse_pdf(self, input_path, filename, prompt_mode, fitz_preprocess=False):

        def _execute_task(task_args):
            return self._parse_single_image(
                **task_args, fitz_preprocess=fitz_preprocess
            )

        print(f"loading pdf: {input_path}")

        images_origin = load_images_from_pdf(input_path, dpi=self.dpi)

        total_pages = len(images_origin)

        tasks = [
            {
                "origin_image": image,
                "prompt_mode": prompt_mode,
                "save_name": filename,
                "source": "pdf",
                "page_idx": i,
            }
            for i, image in enumerate(images_origin)
        ]

        num_thread = min(total_pages, self.num_thread)

        print(f"Parsing PDF with {total_pages} pages using {num_thread} threads...")

        results = []

        with ThreadPool(num_thread) as pool:
            with tqdm(total=total_pages, desc="Processing PDF pages") as pbar:
                for result in pool.imap_unordered(_execute_task, tasks):
                    results.append(result)
                    pbar.update(1)

        results.sort(key=lambda x: x["page_no"])
        for i in range(len(results)):
            results[i]["file_path"] = input_path
        return results

    def parse_file(
        self,
        input_path,
        prompt_mode="prompt_layout_all_en",
        bbox=None,
        fitz_preprocess=False,
    ):
        filename, file_ext = os.path.splitext(os.path.basename(input_path))

        if file_ext == ".pdf":

            results = self.parse_pdf(
                input_path, filename, prompt_mode, fitz_preprocess=True
            )

        elif file_ext in image_extensions:

            results = self.parse_image(
                input_path,
                filename,
                prompt_mode,
                bbox=bbox,
                fitz_preprocess=fitz_preprocess,
            )

        else:
            raise ValueError(
                f"file extension {file_ext} not supported, supported extensions are {image_extensions} and pdf"
            )

        return results
