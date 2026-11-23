
import json
from pathlib import Path
from collections import Counter

# ==================================================
# 1. FILE PATHS
# ==================================================

project_root = Path(__file__).resolve().parent.parent

input_file = (
    project_root
    / "data"
    / "output"
    / "pptx_extracted_text_cleaned.json"
)

# ==================================================
# 2. LOAD CLEANED DATA
# ==================================================

with open(input_file, "r", encoding="utf-8") as file:
    slides = json.load(file)

# ==================================================
# 3. INITIALIZE AUDIT VARIABLES
# ==================================================

total_slides = len(slides)
total_elements = 0

empty_slides = []
empty_elements = []

all_texts = []
unusual_characters = []

# ==================================================
# 4. AUDIT SLIDES AND TEXT ELEMENTS
# ==================================================

for slide in slides:

    slide_number = slide["slide_number"]
    content_list = slide["content"]

    # Check empty slides
    if not content_list:
        empty_slides.append(slide_number)

    for element_index, content in enumerate(content_list, start=1):

        total_elements += 1

        # Check empty text elements
        if not content.strip():
            empty_elements.append(
                {
                    "slide_number": slide_number,
                    "element_index": element_index
                }
            )

        all_texts.append(content)

        # Check unusual control characters
        for char in content:

            if ord(char) < 32 and char not in "\n\t\r":

                unusual_characters.append(
                    {
                        "slide_number": slide_number,
                        "element_index": element_index,
                        "character": repr(char),
                        "unicode": ord(char),
                        "text": content
                    }
                )

# ==================================================
# 5. DETECT DUPLICATE TEXT ENTRIES
# ==================================================

text_counter = Counter(all_texts)

duplicate_entries = {
    text: count
    for text, count in text_counter.items()
    if count > 1
}

# ==================================================
# 6. DISPLAY GENERAL AUDIT RESULTS
# ==================================================

print("========== CLEANED POWERPOINT AUDIT ==========")

print("Total slides:", total_slides)
print("Total text elements:", total_elements)

print("Empty slides:", empty_slides)
print("Empty text elements:", len(empty_elements))

print("Duplicate text entries:", len(duplicate_entries))
print("Remaining unusual control characters:", len(unusual_characters))

# ==================================================
# 7. DISPLAY EMPTY TEXT ELEMENT DETAILS
# ==================================================

if empty_elements:

    print("\n========== EMPTY TEXT ELEMENT DETAILS ==========")

    for element in empty_elements:

        print(
            "Slide:", element["slide_number"],
            "| Element:", element["element_index"]
        )

# ==================================================
# 8. DISPLAY DUPLICATE TEXT DETAILS
# ==================================================

if duplicate_entries:

    print("\n========== DUPLICATE TEXT DETAILS ==========")

    for text, count in duplicate_entries.items():

        print("Count:", count, "| Text:", repr(text))

else:

    print("\nNo duplicate text entries found.")

# ==================================================
# 9. DISPLAY EXACT LOCATIONS OF DUPLICATES
# ==================================================

if duplicate_entries:

    print("\n========== DUPLICATE LOCATIONS ==========")

    duplicate_locations = {}

    for slide in slides:

        slide_number = slide["slide_number"]

        for element_index, content in enumerate(
            slide["content"],
            start=1
        ):

            if content in duplicate_entries:

                duplicate_locations.setdefault(
                    content, []
                ).append(
                    {
                        "slide_number": slide_number,
                        "element_index": element_index
                    }
                )

    for text, locations in duplicate_locations.items():

        print("\nText:", repr(text))

        for location in locations:

            print(
                "Slide:", location["slide_number"],
                "| Element:", location["element_index"]
            )

# ==================================================
# 10. DISPLAY UNUSUAL CHARACTER DETAILS
# ==================================================

if unusual_characters:

    print("\n========== UNUSUAL CHARACTER DETAILS ==========")

    for item in unusual_characters:

        print("\nSlide:", item["slide_number"])
        print("Element:", item["element_index"])
        print("Character:", item["character"])
        print("Unicode:", item["unicode"])
        print("Text:", repr(item["text"]))

else:

    print("\nNo unusual control characters found.")

# ==================================================
# 11. FINAL SUMMARY
# ==================================================

print("\n========== FINAL SUMMARY ==========")

if not empty_slides and not empty_elements:
    print("No empty slides or text elements found.")
else:
    print("Some empty slides or text elements need inspection.")

if not unusual_characters:
    print("Special character normalization: successful.")
else:
    print("Some unusual control characters remain.")

if duplicate_entries:
    print("Duplicate entries detected: manual verification required.")
else:
    print("No duplicate entries detected.")

print("\nAudit completed successfully.")
