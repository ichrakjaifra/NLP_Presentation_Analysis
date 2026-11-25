
import json
from pathlib import Path
from collections import Counter

# Project paths
project_root = Path(__file__).resolve().parent.parent

input_file = (
    project_root
    / "data"
    / "output"
    / "pptx_extracted_text_cleaned.json"
)

# Load extracted text
with open(input_file, "r", encoding="utf-8") as file:
    slides = json.load(file)


print("========== TEXT CLASSIFICATION PREPARATION ==========")

print("Total slides:", len(slides))

total_elements = 0
empty_elements = 0
text_lengths = []

all_texts = []

for slide in slides:

    slide_number = slide["slide_number"]
    contents = slide["content"]

    print(f"\n========== SLIDE {slide_number} ==========")
    print("Number of elements:", len(contents))

    for index, content in enumerate(contents, start=1):

        text = content.strip()

        if not text:
            empty_elements += 1
            continue

        total_elements += 1
        text_lengths.append(len(text))
        all_texts.append(text)

        print(f"\nElement {index}")
        print("Characters:", len(text))
        print("Content:")
        print(text)


print("\n========== FINAL SUMMARY ==========")

print("Total slides:", len(slides))
print("Total text elements:", total_elements)
print("Empty elements:", empty_elements)

if text_lengths:

    print("Shortest element:", min(text_lengths))
    print("Longest element:", max(text_lengths))
    print(
        "Average length:",
        round(sum(text_lengths) / len(text_lengths), 2)
    )

print("\nInspection completed successfully.")
