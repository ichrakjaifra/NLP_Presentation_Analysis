
import json
from pathlib import Path
from collections import Counter

project_root = Path(__file__).resolve().parent.parent

input_file = (
    project_root
    / "data"
    / "output"
    / "pptx_extracted_text.json"
)

with open(input_file, "r", encoding="utf-8") as file:
    slides = json.load(file)

print("========== SPECIAL CHARACTERS ANALYSIS ==========")

total_characters = Counter()

for slide in slides:
    slide_number = slide["slide_number"]

    for content_index, content in enumerate(slide["content"], start=1):

        for char in content:
            if ord(char) < 32 and char not in "\n\t\r":

                total_characters[repr(char)] += 1

                print("\nSlide:", slide_number)
                print("Content element:", content_index)
                print("Character:", repr(char))
                print("Unicode code:", ord(char))
                print("Text:", repr(content))

print("\n========== SUMMARY ==========")

for character, count in total_characters.items():
    print(character, ":", count)

print("Total unusual characters:", sum(total_characters.values()))
