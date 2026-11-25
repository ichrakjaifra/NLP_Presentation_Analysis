
from pptx import Presentation
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
input_file = project_root / "data" / "input" / "presentation_test.pptx"

presentation = Presentation(input_file)

print("========== POWERPOINT NOTES INSPECTION ==========")
print("Total slides:", len(presentation.slides))

slides_with_notes = 0
slides_without_notes = 0
total_notes_characters = 0

for slide_number, slide in enumerate(presentation.slides, start=1):

    notes_text = ""

    try:
        notes_slide = slide.notes_slide
        notes_text_frame = notes_slide.notes_text_frame

        if notes_text_frame is not None:
            notes_text = notes_text_frame.text.strip()

    except Exception as error:
        print(f"\nSlide {slide_number}: Error - {error}")
        continue

    print(f"\n========== SLIDE {slide_number} ==========")

    if notes_text:
        slides_with_notes += 1
        total_notes_characters += len(notes_text)

        print("Notes found: YES")
        print("Notes content:")
        print(notes_text)

    else:
        slides_without_notes += 1
        print("Notes found: NO")

print("\n========== FINAL SUMMARY ==========")
print("Total slides:", len(presentation.slides))
print("Slides with notes:", slides_with_notes)
print("Slides without notes:", slides_without_notes)
print("Total notes characters:", total_notes_characters)

print("\nInspection completed.")
