
from pathlib import Path
import json
import re

# 1. Get the project directory
project_root = Path(__file__).resolve().parent.parent

# 2. Define input and output paths
input_path = (
    project_root / "data" / "output" / "structured_pages_cleaned.json"
)

output_path = (
    project_root / "data" / "output" / "text_blocks.json"
)

# 3. Check if the input file exists
if not input_path.exists():
    print("Error: Cleaned structured JSON file not found!")
    print("Expected file location:", input_path)

else:
    # 4. Read the structured document
    with input_path.open("r", encoding="utf-8") as input_file:
        document = json.load(input_file)

    structured_pages = []
    total_blocks = 0

    # 5. Process each page
    for page in document["pages"]:

        page_number = page["page_number"]
        page_content = page["content"]

        # 6. Split the page content using empty lines
        raw_blocks = re.split(r"\n\s*\n", page_content)

        page_blocks = []

        # 7. Clean and organize each text block
        for raw_block in raw_blocks:

            lines = [
                line.strip()
                for line in raw_block.splitlines()
                if line.strip()
            ]

            # Join the lines belonging to the same block
            block_content = " ".join(lines)

            # Ignore empty blocks
            if block_content:
                block_id = f"page_{page_number}_block_{len(page_blocks) + 1}"

                page_blocks.append({
                    "block_id": block_id,
                    "content": block_content
                })

        total_blocks += len(page_blocks)

        # 8. Store the blocks with their page number
        structured_pages.append({
            "page_number": page_number,
            "blocks": page_blocks
        })

    # 9. Create the final structured document
    result = {
        "source_file": document["source_file"],
        "number_of_pages": document["number_of_pages"],
        "number_of_blocks": total_blocks,
        "pages": structured_pages
    }

    # 10. Save the result
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8") as output_file:
        json.dump(result, output_file, ensure_ascii=False, indent=4)

    # 11. Display the results
    print("Text block segmentation completed successfully!")
    print("Number of pages:", len(structured_pages))
    print("Number of text blocks:", total_blocks)
    print("Output saved to:", output_path)
