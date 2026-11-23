
from pathlib import Path
import json
import pymupdf

project_root = Path(__file__).resolve().parent.parent

input_path = project_root / "data" / "output" / "pdf_text_blocks.json"
pdf_path = project_root / "data" / "input" / "presentation_test.pdf"
output_path = project_root / "data" / "output" / "pdf_text_blocks_cleaned.json"

if not input_path.exists() or not pdf_path.exists():
    print("Error: Required input file not found!")

else:
    with input_path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    pdf_document = pymupdf.open(pdf_path)

    removed_footer = 0
    removed_page_numbers = 0

    for page_data in data["pages"]:
        page_number = page_data["page_number"]
        page_height = pdf_document[page_number - 1].rect.height

        cleaned_blocks = []

        for block in page_data["blocks"]:
            content = block["content"].strip()
            y0 = block["bbox"]["y0"]

            # Remove the repeated lecture footer
            if content == "6.100L Lecture 1":
                removed_footer += 1
                continue

            # Remove the page number only at the bottom of the page
            if content == str(page_number) and y0 >= page_height * 0.85:
                removed_page_numbers += 1
                continue

            cleaned_blocks.append(block)

        page_data["blocks"] = cleaned_blocks

    pdf_document.close()

    data["number_of_blocks"] = sum(
        len(page["blocks"]) for page in data["pages"]
    )

    data["processing"] = {
        "removed_footer": "6.100L Lecture 1",
        "removed_footer_occurrences": removed_footer,
        "removed_page_numbers": removed_page_numbers
    }

    with output_path.open("w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

    print("Text block cleaning completed successfully!")
    print("Number of pages:", len(data["pages"]))
    print("Remaining text blocks:", data["number_of_blocks"])
    print("Removed footer occurrences:", removed_footer)
    print("Removed page numbers:", removed_page_numbers)
    print("Output saved to:", output_path)
