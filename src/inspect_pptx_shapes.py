
from pptx import Presentation
from pptx.enum.shapes import MSO_SHAPE_TYPE
from pathlib import Path
from collections import Counter

# ==================================================
# 1. FILE PATHS
# ==================================================

project_root = Path(__file__).resolve().parent.parent

input_file = (
    project_root
    / "data"
    / "input"
    / "presentation_test.pptx"
)

# ==================================================
# 2. LOAD PRESENTATION
# ==================================================

presentation = Presentation(input_file)

# ==================================================
# 3. SHAPE INSPECTION FUNCTION
# ==================================================

def inspect_shapes(shapes, counter, details, slide_number, level=0):

    for shape in shapes:

        shape_type = str(shape.shape_type)

        counter[shape_type] += 1

        details.append({
            "slide_number": slide_number,
            "shape_name": shape.name,
            "shape_type": shape_type,
            "nesting_level": level,
            "has_text_frame": shape.has_text_frame,
            "has_table": shape.has_table,
            "has_chart": shape.has_chart
        })

        # Inspect grouped shapes recursively
        if shape.shape_type == MSO_SHAPE_TYPE.GROUP:

            inspect_shapes(
                shape.shapes,
                counter,
                details,
                slide_number,
                level + 1
            )

# ==================================================
# 4. INSPECT ALL SLIDES
# ==================================================

global_counter = Counter()
all_details = []

print("========== POWERPOINT SHAPES ANALYSIS ==========")

print("Total slides:", len(presentation.slides))

for slide_number, slide in enumerate(
    presentation.slides,
    start=1
):

    slide_counter = Counter()
    slide_details = []

    inspect_shapes(
        slide.shapes,
        slide_counter,
        slide_details,
        slide_number
    )

    global_counter.update(slide_counter)
    all_details.extend(slide_details)

    print(f"\n========== SLIDE {slide_number} ==========")

    print("Number of top-level shapes:", len(slide.shapes))

    for shape_type, count in slide_counter.items():

        print(shape_type, ":", count)

# ==================================================
# 5. GLOBAL SUMMARY
# ==================================================

print("\n========== GLOBAL SHAPES SUMMARY ==========")

for shape_type, count in global_counter.items():

    print(shape_type, ":", count)

print("\nTotal shapes including grouped contents:",
      sum(global_counter.values()))

# ==================================================
# 6. SPECIAL ELEMENTS SUMMARY
# ==================================================

print("\n========== SPECIAL ELEMENTS ==========")

for detail in all_details:

    if (
        detail["has_table"]
        or detail["has_chart"]
        or detail["shape_type"] in [
            str(MSO_SHAPE_TYPE.PICTURE),
            str(MSO_SHAPE_TYPE.GROUP),
        ]
    ):

        print(
            "Slide:", detail["slide_number"],
            "| Name:", detail["shape_name"],
            "| Type:", detail["shape_type"],
            "| Table:", detail["has_table"],
            "| Chart:", detail["has_chart"],
            "| Group level:", detail["nesting_level"]
        )

print("\nAnalysis completed successfully.")
