
import json
from pathlib import Path
from jsonschema import Draft202012Validator


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

OUTPUT_DIR = PROJECT_ROOT / "data" / "output"
UNIFIED_DIR = OUTPUT_DIR / "unified"
SCHEMA_FILE = PROJECT_ROOT / "schema" / "unified_schema_v0_1.json"

PDF_INPUT = OUTPUT_DIR / "classified_text_blocks_v2.json"

PPTX_TEXT_INPUT = OUTPUT_DIR / "pptx_classified_text.json"
PPTX_IMAGES_INPUT = OUTPUT_DIR / "pptx_images_report.json"


# ============================================================
# GENERAL HELPERS
# ============================================================

def load_json(path):
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def save_json(data, path):
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


def normalize_subtype(category):
    if not category:
        return None

    return category.replace("_candidate", "")


def create_classification(category, reason):
    if not category:
        return None

    return {
        "category": category,
        "method": "rule_based",
        "reason": reason
    }


def create_source(method, original_id):
    return {
        "extraction_method": method,
        "is_ocr": False,
        "original_element_id": str(original_id)
        if original_id is not None else None
    }


# ============================================================
# PDF CONVERSION
# ============================================================

def convert_pdf():

    print("\n========== PDF CONVERSION ==========")

    pdf_data = load_json(PDF_INPUT)

    pages = pdf_data.get("pages", [])

    units = []

    for page in pages:

        page_number = page.get("page_number")

        elements = []

        blocks = page.get("blocks", [])

        for index, block in enumerate(blocks, start=1):

            block_id = block.get(
                "block_id",
                f"page_{page_number}_block_{index}"
            )

            content = block.get("content", "")

            category = block.get("predicted_type")
            reason = block.get("classification_reason")

            bbox = block.get("bbox")

            position = None

            if isinstance(bbox, dict):

                x0 = bbox.get("x0")
                y0 = bbox.get("y0")
                x1 = bbox.get("x1")
                y1 = bbox.get("y1")

                if all(
                    isinstance(value, (int, float))
                    for value in [x0, y0, x1, y1]
                ):

                    position = {
                        "x": x0,
                        "y": y0,
                        "width": x1 - x0,
                        "height": y1 - y0,
                        "unit": "point",
                        "coordinate_system": "page"
                    }

            element = {
                "element_id": str(block_id),
                "order": index,
                "type": "text",
                "subtype": normalize_subtype(category),
                "text": content,
                "classification": create_classification(
                    category,
                    reason
                ),
                "source": create_source(
                    pdf_data.get(
                        "extraction_method",
                        "PyMuPDF get_text blocks"
                    ),
                    block_id
                ),
                "position": position
            }

            elements.append(element)

        unit = {
            "unit_id": f"page_{page_number}",
            "unit_number": page_number,
            "unit_type": "page",
            "elements": elements
        }

        units.append(unit)

    # Document metadata
    document = {
        "document_id": "presentation_test_pdf",
        "filename": pdf_data.get(
            "source_file",
            "presentation_test.pdf"
        ),
        "format": "pdf",
        "number_of_units": len(units),
        "metadata": {
            "number_of_blocks": pdf_data.get(
                "number_of_blocks"
            )
        }
    }

    unified_data = {
        "schema_version": "0.1",
        "document": document,
        "units": units
    }

    output_file = UNIFIED_DIR / "presentation_test_unified_pdf.json"

    save_json(unified_data, output_file)

    print("PDF pages:", len(units))

    print("PDF elements:", sum(
        len(unit["elements"]) for unit in units
    ))

    print("Output:", output_file.name)

    return unified_data


# ============================================================
# PPTX INPUT NORMALIZATION
# ============================================================

def get_pptx_slides(data):

    if isinstance(data, list):
        return data

    if isinstance(data, dict):

        for key in ["slides", "data", "results"]:

            if isinstance(data.get(key), list):
                return data[key]

    raise ValueError(
        "Unexpected PPTX classified JSON structure."
    )


def get_pptx_images(data):

    if isinstance(data, list):
        return data

    if isinstance(data, dict):

        for key in ["images", "pictures", "data", "results"]:

            if isinstance(data.get(key), list):
                return data[key]

    raise ValueError(
        "Unexpected PPTX images report structure."
    )


# ============================================================
# PPTX CONVERSION
# ============================================================

def convert_pptx():

    print("\n========== PPTX CONVERSION ==========")

    pptx_data = load_json(PPTX_TEXT_INPUT)

    images_data = load_json(PPTX_IMAGES_INPUT)

    slides = get_pptx_slides(pptx_data)

    images = get_pptx_images(images_data)

    # Group images by slide number
    images_by_slide = {}

    for image in images:

        slide_number = image.get("slide_number")

        images_by_slide.setdefault(
            slide_number, []
        ).append(image)

    units = []

    for slide in slides:

        slide_number = slide.get("slide_number")

        elements = []

        content_items = slide.get("content", [])

        # Convert text elements
        for index, item in enumerate(content_items, start=1):

            element_id = item.get(
                "element_id",
                f"slide_{slide_number}_element_{index}"
            )

            text_content = item.get("text", "")

            category = item.get("category")

            reason = item.get("reason")

            element = {
                "element_id": str(element_id),
                "order": index,
                "type": "text",
                "subtype": normalize_subtype(category),
                "text": text_content,
                "classification": create_classification(
                    category,
                    reason
                ),
                "source": create_source(
                    "python-pptx",
                    element_id
                ),
                "position": None
            }

            elements.append(element)

        # Add extracted images belonging to this slide
        slide_images = images_by_slide.get(slide_number, [])

        for image_index, image_info in enumerate(
            slide_images,
            start=1
        ):

            image_number = image_info.get(
                "image_number",
                image_index
            )

            image_id = (
                f"slide_{slide_number}_image_{image_number}"
            )

            left = image_info.get("left")

            top = image_info.get("top")

            width = image_info.get("width")

            height = image_info.get("height")

            position = None

            if all(
                isinstance(value, (int, float))
                for value in [left, top, width, height]
            ):

                position = {
                    "x": left,
                    "y": top,
                    "width": width,
                    "height": height,
                    "unit": "EMU",
                    "coordinate_system": "slide"
                }

            image_element = {
                "element_id": image_id,
                "order": len(elements) + 1,
                "type": "image",
                "subtype": "illustration",
                "text": None,
                "source": create_source(
                    "python-pptx image extraction",
                    image_id
                ),
                "position": position,
                "metadata": {
                    "filename": image_info.get("filename"),
                    "content_type": image_info.get("content_type"),
                    "width": width,
                    "height": height,
                    "size_bytes": image_info.get("size_bytes"),
                    "shape_name": image_info.get("shape_name")
                }
            }

            elements.append(image_element)

        unit = {
            "unit_id": f"slide_{slide_number}",
            "unit_number": slide_number,
            "unit_type": "slide",
            "elements": elements
        }

        units.append(unit)

    # Document metadata
    document = {
        "document_id": "presentation_test_pptx",
        "filename": "presentation_test.pptx",
        "format": "pptx",
        "number_of_units": len(units),
        "metadata": {
            "number_of_images": len(images)
        }
    }

    unified_data = {
        "schema_version": "0.1",
        "document": document,
        "units": units
    }

    output_file = UNIFIED_DIR / "presentation_test_unified_pptx.json"

    save_json(unified_data, output_file)

    print("PPTX slides:", len(units))

    print("PPTX text elements:", sum(
        1 for unit in units
        for element in unit["elements"]
        if element["type"] == "text"
    ))

    print("PPTX images:", sum(
        1 for unit in units
        for element in unit["elements"]
        if element["type"] == "image"
    ))

    print("Output:", output_file.name)

    return unified_data


# ============================================================
# UNIFIED SCHEMA VALIDATION
# ============================================================

def validate_output(data, filename, validator):

    errors = sorted(
        validator.iter_errors(data),
        key=lambda error: list(error.path)
    )

    if errors:

        print(f"\n{filename}: INVALID")

        for error in errors:

            location = " -> ".join(
                str(part) for part in error.path
            )

            print("Error location:", location or "root")

            print("Reason:", error.message)

        return False

    print(f"\n{filename}: VALID")

    return True


# ============================================================
# MAIN
# ============================================================

def main():

    print("===================================================")

    print("PDF AND PPTX UNIFIED JSON CONVERTER")

    print("===================================================")

    UNIFIED_DIR.mkdir(parents=True, exist_ok=True)

    schema = load_json(SCHEMA_FILE)

    Draft202012Validator.check_schema(schema)

    validator = Draft202012Validator(schema)

    pdf_unified = convert_pdf()

    pptx_unified = convert_pptx()

    print("\n========== UNIFIED VALIDATION ==========")

    pdf_valid = validate_output(
        pdf_unified,
        "PDF Unified JSON",
        validator
    )

    pptx_valid = validate_output(
        pptx_unified,
        "PPTX Unified JSON",
        validator
    )

    print("\n===================================================")

    if pdf_valid and pptx_valid:

        print("ALL CONVERSIONS AND VALIDATIONS SUCCESSFUL")

    else:

        print("VALIDATION ERRORS FOUND")

    print("===================================================")


if __name__ == "__main__":
    main()
