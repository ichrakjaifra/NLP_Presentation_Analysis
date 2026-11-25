
from pptx import Presentation
from pptx.enum.shapes import MSO_SHAPE_TYPE
from pathlib import Path
import json

# Project paths
project_root = Path(__file__).resolve().parent.parent

input_file = project_root / "data" / "input" / "presentation_test.pptx"
images_dir = project_root / "data" / "images"
output_file = project_root / "data" / "output" / "pptx_images_report.json"

# Load presentation
presentation = Presentation(input_file)

# Create output directories
images_dir.mkdir(parents=True, exist_ok=True)
output_file.parent.mkdir(parents=True, exist_ok=True)


def extract_picture_shapes(shapes):
    """
    Extract picture shapes recursively,
    including pictures inside Group Shapes.
    """
    pictures = []

    for shape in shapes:

        if shape.shape_type == MSO_SHAPE_TYPE.GROUP:
            pictures.extend(
                extract_picture_shapes(shape.shapes)
            )

        elif shape.shape_type == MSO_SHAPE_TYPE.PICTURE:
            pictures.append(shape)

    return pictures


# Store image metadata
images_data = []
total_images = 0

print("========== POWERPOINT IMAGES INSPECTION ==========")
print("Total slides:", len(presentation.slides))


# Process each slide
for slide_number, slide in enumerate(presentation.slides, start=1):

    pictures = extract_picture_shapes(slide.shapes)

    print(f"\n========== SLIDE {slide_number} ==========")
    print("Images found:", len(pictures))

    for image_number, shape in enumerate(pictures, start=1):

        image = shape.image

        # Image information
        extension = image.ext
        image_filename = (
            f"slide_{slide_number:02d}_image_{image_number:02d}.{extension}"
        )

        image_path = images_dir / image_filename

        # Extract original image
        image_path.write_bytes(image.blob)

        # Save image metadata
        image_info = {
            "slide_number": slide_number,
            "image_number": image_number,
            "shape_name": shape.name,
            "filename": image_filename,
            "content_type": image.content_type,
            "width": image.size[0],
            "height": image.size[1],
            "left": shape.left,
            "top": shape.top,
            "size_bytes": len(image.blob)
        }

        images_data.append(image_info)
        total_images += 1

        print("Image:", image_filename)
        print("Content type:", image.content_type)
        print("Dimensions:", image.size[0], "x", image.size[1])
        print("Size:", len(image.blob), "bytes")


# Save JSON report
with open(output_file, "w", encoding="utf-8") as file:
    json.dump(images_data, file, ensure_ascii=False, indent=4)


# Final summary
print("\n========== FINAL SUMMARY ==========")
print("Total slides:", len(presentation.slides))
print("Total images extracted:", total_images)
print("Images directory:", images_dir)
print("JSON report:", output_file)

print("\nImage extraction completed successfully.")
