
import json
from pathlib import Path
from collections import Counter


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

UNIFIED_DIR = PROJECT_ROOT / "data" / "output" / "unified"

PDF_FILE = UNIFIED_DIR / "presentation_test_unified_pdf.json"
PPTX_FILE = UNIFIED_DIR / "presentation_test_unified_pptx.json"


# ============================================================
# HELPERS
# ============================================================

def load_json(path):

    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def audit_document(path, expected_format):

    print("\n" + "=" * 60)
    print(f"AUDIT: {path.name}")
    print("=" * 60)

    if not path.exists():
        print("ERROR: File not found.")
        return

    data = load_json(path)

    document = data.get("document", {})
    units = data.get("units", [])

    all_elements = [
        element
        for unit in units
        for element in unit.get("elements", [])
    ]

    # --------------------------------------------------------
    # DOCUMENT INFORMATION
    # --------------------------------------------------------

    print("\n[1] DOCUMENT INFORMATION")

    print("Document ID:", document.get("document_id"))
    print("Filename:", document.get("filename"))
    print("Format:", document.get("format"))
    print("Schema version:", data.get("schema_version"))

    print("Expected format:", expected_format)

    print(
        "Declared units:",
        document.get("number_of_units")
    )

    print("Actual units:", len(units))

    # --------------------------------------------------------
    # ELEMENT COUNTS
    # --------------------------------------------------------

    print("\n[2] ELEMENT COUNTS")

    type_counts = Counter(
        element.get("type")
        for element in all_elements
    )

    print("Total elements:", len(all_elements))

    for element_type, count in sorted(type_counts.items()):
        print(f"{element_type}: {count}")

    # --------------------------------------------------------
    # CLASSIFICATION COUNTS
    # --------------------------------------------------------

    print("\n[3] CLASSIFICATION")

    categories = Counter(
        element.get("classification", {}).get("category")
        for element in all_elements
        if isinstance(element.get("classification"), dict)
    )

    for category, count in sorted(categories.items()):
        print(f"{category}: {count}")

    unclassified = sum(
        1 for element in all_elements
        if element.get("classification") is None
    )

    print("Unclassified elements:", unclassified)

    # --------------------------------------------------------
    # ID AND ORDER CHECKS
    # --------------------------------------------------------

    print("\n[4] IDENTIFIERS AND ORDER")

    duplicate_unit_ids = []
    duplicate_element_ids = []
    invalid_orders = []

    unit_ids = [
        unit.get("unit_id")
        for unit in units
    ]

    unit_id_counts = Counter(unit_ids)

    duplicate_unit_ids = [
        item for item, count in unit_id_counts.items()
        if count > 1
    ]

    for unit in units:

        elements = unit.get("elements", [])

        element_ids = [
            element.get("element_id")
            for element in elements
        ]

        id_counts = Counter(element_ids)

        for element_id, count in id_counts.items():

            if count > 1:
                duplicate_element_ids.append(
                    (unit.get("unit_id"), element_id)
                )

        orders = [
            element.get("order")
            for element in elements
        ]

        if orders != list(range(1, len(elements) + 1)):
            invalid_orders.append(unit.get("unit_id"))

    print("Duplicate unit IDs:", len(duplicate_unit_ids))
    print("Duplicate element IDs:", len(duplicate_element_ids))
    print("Units with invalid order:", len(invalid_orders))

    # --------------------------------------------------------
    # TEXT CHECKS
    # --------------------------------------------------------

    print("\n[5] TEXT CHECKS")

    text_elements = [
        element for element in all_elements
        if element.get("type") == "text"
    ]

    empty_text = sum(
        1 for element in text_elements
        if not isinstance(element.get("text"), str)
        or not element.get("text").strip()
    )

    print("Text elements:", len(text_elements))
    print("Empty text elements:", empty_text)

    # --------------------------------------------------------
    # POSITION CHECKS
    # --------------------------------------------------------

    print("\n[6] POSITION CHECKS")

    elements_with_position = sum(
        1 for element in all_elements
        if isinstance(element.get("position"), dict)
    )

    elements_without_position = (
        len(all_elements) - elements_with_position
    )

    print("Elements with position:", elements_with_position)
    print("Elements without position:", elements_without_position)

    # --------------------------------------------------------
    # IMAGE CHECKS
    # --------------------------------------------------------

    print("\n[7] IMAGE CHECKS")

    image_elements = [
        element for element in all_elements
        if element.get("type") == "image"
    ]

    images_missing_metadata = sum(
        1 for element in image_elements
        if not isinstance(element.get("metadata"), dict)
    )

    images_missing_dimensions = sum(
        1 for element in image_elements
        if not isinstance(element.get("metadata"), dict)
        or element["metadata"].get("width") is None
        or element["metadata"].get("height") is None
    )

    print("Images:", len(image_elements))
    print("Images missing metadata:", images_missing_metadata)
    print("Images missing dimensions:", images_missing_dimensions)

    # --------------------------------------------------------
    # SOURCE CHECKS
    # --------------------------------------------------------

    print("\n[8] SOURCE CHECKS")

    missing_source = sum(
        1 for element in all_elements
        if not isinstance(element.get("source"), dict)
    )

    missing_extraction_method = sum(
        1 for element in all_elements
        if not isinstance(element.get("source"), dict)
        or not element["source"].get("extraction_method")
    )

    print("Elements missing source:", missing_source)
    print(
        "Elements missing extraction method:",
        missing_extraction_method
    )

    # --------------------------------------------------------
    # SUMMARY
    # --------------------------------------------------------

    print("\n[9] AUDIT SUMMARY")

    checks = {
        "Correct format": document.get("format") == expected_format,
        "Correct unit count": document.get("number_of_units") == len(units),
        "Unique unit IDs": len(duplicate_unit_ids) == 0,
        "Unique element IDs per unit": len(duplicate_element_ids) == 0,
        "Valid element order": len(invalid_orders) == 0,
        "All elements have source": missing_source == 0,
        "All sources have extraction method": missing_extraction_method == 0
    }

    for check, passed in checks.items():
        print(f"{check}: {'PASS' if passed else 'FAIL'}")

    print("\nAudit completed.")


# ============================================================
# MAIN
# ============================================================

def main():

    print("============================================================")
    print("UNIFIED JSON CONTENT AUDIT")
    print("============================================================")

    audit_document(PDF_FILE, "pdf")

    audit_document(PPTX_FILE, "pptx")

    print("\n============================================================")
    print("ALL AUDITS COMPLETED")
    print("============================================================")


if __name__ == "__main__":
    main()
