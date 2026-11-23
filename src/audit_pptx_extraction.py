
import json
from pathlib import Path
from collections import Counter

project_root = Path(__file__).resolve().parent.parent
input_file = project_root / "data" / "output" / "pptx_extracted_text.json"

with open(input_file, "r", encoding="utf-8") as file:
    slides = json.load(file)

print("========== POWERPOINT EXTRACTION AUDIT ==========")
print("Total slides:", len(slides))

empty_slides = []
duplicate_texts = []
control_characters = []

for slide in slides:
    slide_number = slide["slide_number"]
    contents = slide["content"]

    if not contents:
        empty_slides.append(slide_number)

    counts = Counter(contents)
    for text, count in counts.items():
        if count > 1:
            duplicate_texts.append((slide_number, text, count))

    for content in contents:
        for char in content:
            if ord(char) < 32 and char not in "\n\t\r":
                control_characters.append(
                    (slide_number, repr(char), ord(char))
                )

print("\nSlides with no extracted text:", empty_slides)
print("Number of duplicate text entries:", len(duplicate_texts))
print("Number of unusual control characters:", len(control_characters))

print("\n---------- CONTENT PER SLIDE ----------")
for slide in slides:
    print(
        f"Slide {slide['slide_number']}: "
        f"{len(slide['content'])} text elements"
    )

print("\n---------- DUPLICATES ----------")
for item in duplicate_texts:
    print(item)

print("\n---------- CONTROL CHARACTERS ----------")
for item in control_characters:
    print(item)

print("\nAudit completed.")
