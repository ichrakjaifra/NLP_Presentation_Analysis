
import json
import re
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent

INPUT_FILE = PROJECT_ROOT / "data" / "output" / "pdf_text_blocks_cleaned.json"
OUTPUT_FILE = PROJECT_ROOT / "data" / "output" / "classified_text_blocks.json"


def classify_block(content):
    text = content.strip()

    if not text:
        return "other"

    lines = [line.strip() for line in text.splitlines() if line.strip()]

    # 1. Detect list items or numbered steps
    if re.search(r"(^|\n)\s*(|-|\*|\d+[\).])\s*", text):
        return "list_candidate"

    # 2. Detect possible table content
    if len(lines) >= 3:
        numeric_lines = sum(
            1 for line in lines
            if re.fullmatch(r"[\d./\-]+", line.strip())
        )

        if numeric_lines >= 2:
            return "table_candidate"

    # 3. Detect short uppercase titles or labels
    if len(text) <= 60 and text.isupper():
        return "title_or_label_candidate"

    # 4. Detect short labels
    if len(text) <= 30 and len(lines) <= 2:
        return "short_label_candidate"

    # 5. Default category
    return "paragraph_candidate"


def main():
    with open(INPUT_FILE, "r", encoding="utf-8") as file:
        data = json.load(file)

    # Support either a list of pages or a dictionary containing pages
    if isinstance(data, list):
        pages = data
    elif isinstance(data, dict) and "pages" in data:
        pages = data["pages"]
    else:
        raise ValueError("Unexpected JSON structure. Check the input file.")

    summary = {}
    total_blocks = 0

    for page in pages:
        for block in page.get("blocks", []):
            category = classify_block(block.get("content", ""))

            block["predicted_type"] = category

            summary[category] = summary.get(category, 0) + 1
            total_blocks += 1

    output_data = {
        "method": "Rule-based classification",
        "total_pages": len(pages),
        "total_blocks": total_blocks,
        "classification_summary": summary,
        "pages": pages
    }

    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        json.dump(output_data, file, ensure_ascii=False, indent=4)

    print("Text block classification completed successfully!")
    print(f"Number of pages: {len(pages)}")
    print(f"Number of classified blocks: {total_blocks}")

    print("\nClassification results:")
    for category, count in summary.items():
        print(f"{category}: {count}")

    print(f"\nOutput saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
