import time
from ocr.parser import DotsOCRParser


def main():
    ocr = DotsOCRParser(
        model_name="model",
        ip="localhost",
        port=8000,
        num_thread=2,
    )

    image_file = "demo/pdfs/Акт на ЗУ марк.pdf"

    start = time.time()
    results = ocr.parse_file(
        input_path=image_file,
        prompt_mode="prompt_layout_all_en",
        fitz_preprocess=True,
        # prompt_mode="prompt_ocr",
    )
    end = time.time()

    print("\n=== OCR Results ===")
    for r in results:
        print(r)
    print(f"\nTime taken: {end - start:.2f} seconds")


if __name__ == "__main__":
    main()
