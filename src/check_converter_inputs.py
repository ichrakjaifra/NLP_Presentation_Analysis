
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
output = project_root / "data" / "output"

required_files = [
    "pdf_text_blocks_cleaned.json",
    "classified_text_blocks_v2.json",
    "pptx_extracted_text_cleaned.json",
    "pptx_classified_text.json",
    "pptx_images_report.json"
]

print("========== CONVERTER INPUT CHECK ==========")

for filename in required_files:
    path = output / filename
    status = "FOUND" if path.exists() else "MISSING"
    print(f"{filename}: {status}")

print("\nCheck finished.")
