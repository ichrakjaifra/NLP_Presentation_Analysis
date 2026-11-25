
import json
from pathlib import Path

# ============================================================
# 1. Project paths
# ============================================================

project_root = Path(__file__).resolve().parent.parent

input_file = (
    project_root
    / "data"
    / "output"
    / "pptx_classified_text.json"
)

# ============================================================
# 2. Load classified data
# ============================================================

with open(input_file, "r", encoding="utf-8") as file:
    slides = json.load(file)

# Slides selected for manual qualitative inspection
selected_slides = [1, 3, 5, 7, 18, 19, 21, 22, 23, 24]

# ============================================================
# 3. Audit classification
# ============================================================

print("========== CLASSIFICATION AUDIT ==========")

for slide in slides:

    slide_number = slide["slide_number"]

    if slide_number not in selected_slides:
        continue

    print(f"\n========== SLIDE {slide_number} ==========")

    for element in slide["content"]:

        print("\nElement:", element["element_id"])
        print("Category:", element["category"])
        print("Reason:", element["reason"])
        print("Text:", element["text"])
        print("-" * 60)

# ============================================================
# 4. Final summary
# ============================================================

print("\nAudit completed successfully.")
