
import json
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
output_folder = project_root / "data" / "output"


def load_json(filename):
    path = output_folder / filename

    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


print("=" * 60)
print("PDF COMPLEX CASES")
print("=" * 60)

pdf_data = load_json("classified_text_blocks_v2.json")

for page in pdf_data["pages"]:
    if page["page_number"] in [4, 8, 9, 10, 18]:
        print(f"\n--- PDF PAGE {page['page_number']} ---")

        for block in page["blocks"]:
            print("\nID:", block["block_id"])
            print("Type:", block["predicted_type"])
            print("Text:", repr(block["content"][:300]))


print("\n" + "=" * 60)
print("POWERPOINT COMPLEX CASES")
print("=" * 60)

pptx_data = load_json("pptx_classified_text.json")

for slide in pptx_data:
    if slide["slide_number"] in [5, 18, 21, 22, 23, 24]:
        print(f"\n--- PPTX SLIDE {slide['slide_number']} ---")

        for element in slide["content"]:
            print("\nID:", element["element_id"])
            print("Category:", element["category"])
            print("Text:", repr(element["text"][:300]))


print("\n" + "=" * 60)
print("IMAGE REPORT")
print("=" * 60)

image_data = load_json("pptx_images_report.json")

for image in image_data:
    if image["slide_number"] in [5, 18]:
        print(
            f"Slide {image['slide_number']} | "
            f"{image['filename']} | "
            f"{image['width']}x{image['height']}"
        )

print("\nInspection finished.")
