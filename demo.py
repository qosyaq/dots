import time
from ocr.parser import DotsOCRParser
from qwen.inference import inference as qwen_inference
import shutil
from qwen.prompt import prompt_get_all
import json
from excel.excel_prepaire import save_extraction_result_xlsx
import argparse


def main():
    parser = argparse.ArgumentParser(description="OCR and Information Extraction Demo")
    parser.add_argument("--path", "-p", type=str, help="Path to the input PDF file")
    args = parser.parse_args()
    ocr = DotsOCRParser(
        model_name="dots_ocr",
        ip="localhost",
        port=8000,
        num_thread=1,
        dpi=200,
    )
    if args.path:
        input_file = args.path
    else:
        input_file = "demo/pdfs/Жана КХ/Договор аренды.pdf"

    shutil.rmtree("results", ignore_errors=True)

    start1 = time.time()
    results = ocr.parse_file(
        input_path=input_file,
        prompt_mode="prompt_layout_all_en",
        fitz_preprocess=True,
        # prompt_mode="prompt_ocr",
    )
    end1 = time.time()
    print(f"\n[OCR] Time taken: {end1 - start1:.2f} seconds")

    batch = [
        {"page_no": r.get("page_no", 0), "text": r.get("text", "").strip()}
        for r in results
    ]

    start2 = time.time()
    result = qwen_inference(prompt=batch, system_prompt=prompt_get_all)
    end2 = time.time()
    print(f"\n[EXTR] Time taken: {end2 - start2:.2f} seconds")

    total_time = end2 - start1

    print(f"\n[TIME TOTAL] : {total_time:.2f} sec")
    json_output = json.loads(result)
    print("\n[RESULT] :\n", json_output)

    with open("results/batch.json", "w", encoding="utf-8") as f:
        json.dump(batch, f, ensure_ascii=False, indent=4)

    save_extraction_result_xlsx(
        data=json_output, total_time=total_time, file_path=input_file
    )


if __name__ == "__main__":
    main()
