import time
from ocr.parser import DotsOCRParser


def main():
    ocr = DotsOCRParser(
        model_name="dots_ocr",
        ip="localhost",
        port=8000,
        num_thread=2,
        dpi=200,
    )
    input_file = "demo/pdfs/Постановление акима марк.pdf"

    start = time.time()
    results = ocr.parse_file(
        input_path=input_file,
        prompt_mode="prompt_layout_all_en",
        fitz_preprocess=True,
        # prompt_mode="prompt_ocr",
    )
    end = time.time()

    print("\n=== OCR Results ===")
    for r in results:
        print(
            "\n----------------------------------------------------- Page",
            r.get("page_no", -1),
            "-----------------------------------------------------",
        )
        print(r.get("text", ""))
        if "duration" in r:
            print(f"(Processed in {r['duration']:.2f} seconds on thread {r['thread']})")
    print(f"\nTime taken: {end - start:.2f} seconds")


if __name__ == "__main__":
    main()
