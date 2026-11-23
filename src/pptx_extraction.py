
from pptx import Presentation
from pptx.enum.shapes import MSO_SHAPE_TYPE
import json
from pathlib import Path


# 1. Define input and output paths
project_root = Path(__file__).resolve().parent.parent

input_file = project_root / "data" / "input" / "presentation_test.pptx"
output_file = project_root / "data" / "output" / "pptx_extracted_text.json"


# 2. Function for recursive text extraction
def extract_text_from_shapes(shapes):

    texts = []

    for shape in shapes:

        # Check if the shape is a group
        if shape.shape_type == MSO_SHAPE_TYPE.GROUP:

            # Explore the shapes inside the group
            texts.extend(extract_text_from_shapes(shape.shapes))

        # Extract text from normal shapes
        elif shape.has_text_frame:

            text = shape.text.strip()

            if text:
                texts.append(text)

    return texts


# 3. Open the PowerPoint presentation
presentation = Presentation(input_file)


# 4. Extract text from each slide
slides_data = []

for slide_number, slide in enumerate(presentation.slides, start=1):

    slide_texts = extract_text_from_shapes(slide.shapes)

    slide_data = {
        "slide_number": slide_number,
        "content": slide_texts
    }

    slides_data.append(slide_data)


# 5. Create output directory if needed
output_file.parent.mkdir(parents=True, exist_ok=True)


# 6. Save extracted text as JSON
with open(output_file, "w", encoding="utf-8") as file:

    json.dump(
        slides_data,
        file,
        ensure_ascii=False,
        indent=4
    )


# 7. Display results
print("PowerPoint recursive extraction completed successfully")
print("Number of slides:", len(presentation.slides))
print("Output file:", output_file)
