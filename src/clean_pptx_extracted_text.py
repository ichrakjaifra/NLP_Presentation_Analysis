
import json
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent

input_file = (
    project_root
    / "data"
    / "output"
    / "pptx_extracted_text.json"
)

output_file = (
    project_root
    / "data"
    / "output"
    / "pptx_extracted_text_cleaned.json"
)

with open(input_file, "r", encoding="utf-8") as file:
    slides = json.load(file)

total_replacements = 0

for slide in slides:
    for index, content in enumerate(slide["content"]):

        occurrences = content.count("\x0b")
        total_replacements += occurrences

        slide["content"][index] = content.replace("\x0b", "\n")

output_file.parent.mkdir(parents=True, exist_ok=True)

with open(output_file, "w", encoding="utf-8") as file:
    json.dump(slides, file, ensure_ascii=False, indent=4)

print("========== POWERPOINT TEXT CLEANING ==========")
print("Number of slides:", len(slides))
print("Replaced characters:", total_replacements)
print("Replacement: \x0b -> newline")
print("Output file:", output_file)

remaining = sum(
    content.count("\x0b")
    for slide in slides
    for content in slide["content"]
)

print("Remaining vertical tabs:", remaining)
print("Cleaning completed successfully.")
