
from pathlib import Path
import json
import pymupdf

# 1. Get the project directory
project_root = Path(__file__).resolve().parent.parent

# 2. Define input and output paths
input_path = (
    project_root / "data" / "input" / "presentation_test.pdf"
)

output_path = (
    project_root / "data" / "output" / "pdf_text_blocks.json"
)

# 3. Check if the PDF file exists
if not input_path.exists():
    print("Error: PDF file not found!")
    print("Expected file location:", input_path)

else:
    # 4. Open the original PDF document
    pdf_document = pymupdf.open(input_path)

    structured_pages = []
    total_blocks = 0

    # 5. Process each page
    for page_index, page in enumerate(pdf_document):

        page_number = page_index + 1

        # 6. Extract text blocks using PDF layout information
        raw_blocks = page.get_text("blocks", sort=True)

        page_blocks = []

        # 7. Process each extracted block
        for block in raw_blocks:

            # Get the block information
            x0, y0, x1, y1, text = block[:5]

            # Block type: 0 = text, 1 = image
            block_type = block[6] if len(block) > 6 else 0

            # Keep only text blocks
            if block_type != 0:
                continue

            text = text.strip()

            if not text:
                continue

            block_id = (
                f"page_{page_number}_block_{len(page_blocks) + 1}"
            )

            page_blocks.append({
                "block_id": block_id,
                "content": text,
                "bbox": {
                    "x0": round(x0, 2),
                    "y0": round(y0, 2),
                    "x1": round(x1, 2),
                    "y1": round(y1, 2)
                }
            })

        total_blocks += len(page_blocks)

        structured_pages.append({
            "page_number": page_number,
            "blocks": page_blocks
        })

    # 8. Create the final structured document
    result = {
        "source_file": input_path.name,
        "number_of_pages": len(pdf_document),
        "number_of_blocks": total_blocks,
        "extraction_method": "PyMuPDF get_text('blocks')",
        "pages": structured_pages
    }

    # 9. Save the extracted blocks
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8") as output_file:
        json.dump(result, output_file, ensure_ascii=False, indent=4)

    # 10. Close the PDF
    pdf_document.close()

    # 11. Display the results
    print("PDF text block extraction completed successfully!")
    print("Number of pages:", len(structured_pages))
    print("Number of text blocks:", total_blocks)
    print("Output saved to:", output_path)
