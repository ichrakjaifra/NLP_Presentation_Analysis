
from pathlib import Path
import pymupdf

# 1. Get the project directory
project_root = Path(__file__).resolve().parent.parent

# 2. Define input and output paths
pdf_path = project_root / "data" / "input" / "presentation_test.pdf"
output_path = project_root / "data" / "output" / "extracted_text.txt"

# 3. Check if the input PDF exists
if not pdf_path.exists():
    print("Error: PDF file not found!")
    print("Expected file location:", pdf_path)

else:
    # 4. Open the PDF document
    document = pymupdf.open(pdf_path)

    # 5. Create the output directory if necessary
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # 6. Save the extracted text into a TXT file
    with output_path.open("w", encoding="utf-8") as output_file:

        output_file.write(f"Document: {pdf_path.name}\n")
        output_file.write(f"Number of pages: {len(document)}\n")

        # 7. Extract text page by page
        for page_number, page in enumerate(document, start=1):

            text = page.get_text()

            output_file.write(
                f"\n========== PAGE {page_number} ==========\n"
            )

            output_file.write(text)

    # 8. Get the number of pages before closing the document
    number_of_pages = len(document)

    # 9. Close the PDF document
    document.close()

    # 10. Display the results
    print("Extraction completed successfully!")
    print("Number of pages:", number_of_pages)
    print("Extracted text saved to:", output_path)

