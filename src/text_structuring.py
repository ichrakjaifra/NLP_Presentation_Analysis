
from pathlib import Path
import re
import json


# 1. Get the project directory
project_root = Path(__file__).resolve().parent.parent

# 2. Define input and output paths
input_path = project_root / "data" / "output" / "cleaned_text.txt"
output_path = project_root / "data" / "output" / "structured_pages.json"


# 3. Check if the input file exists
if not input_path.exists():
    print("Error: Cleaned text file not found!")
    print("Expected file location:", input_path)

else:
    # 4. Read the cleaned text
    with input_path.open("r", encoding="utf-8") as input_file:
        text = input_file.read()

    # 5. Find all page separators
    page_pattern = r"^========== PAGE (\d+) ==========$"

    page_matches = list(
        re.finditer(page_pattern, text, re.MULTILINE)
    )

    # 6. Prepare the list of structured pages
    pages = []

    # 7. Extract the content of each page
    for index, match in enumerate(page_matches):

        page_number = int(match.group(1))
        content_start = match.end()

        if index + 1 < len(page_matches):
            content_end = page_matches[index + 1].start()
        else:
            content_end = len(text)

        page_content = text[content_start:content_end].strip()

        pages.append({
            "page_number": page_number,
            "content": page_content
        })

    # 8. Prepare the structured document
    structured_document = {
        "source_file": "presentation_test.pdf",
        "number_of_pages": len(pages),
        "pages": pages
    }

    # 9. Create the output directory if necessary
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # 10. Save the structured data as JSON
    with output_path.open("w", encoding="utf-8") as output_file:
        json.dump(
            structured_document,
            output_file,
            ensure_ascii=False,
            indent=4
        )

    # 11. Display the results
    print("Text structuring completed successfully!")
    print("Number of pages:", len(pages))
    print("Structured data saved to:", output_path)
