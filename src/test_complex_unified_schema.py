
import json
from pathlib import Path
from jsonschema import Draft202012Validator

project_root = Path(__file__).resolve().parent.parent

schema_path = project_root / "schema" / "unified_schema_v0_1.json"

with open(schema_path, "r", encoding="utf-8") as file:
    schema = json.load(file)

validator = Draft202012Validator(schema)

print("=" * 55)
print("COMPLEX UNIFIED SCHEMA TEST")
print("=" * 55)

def create_element(element_id, order, element_type, subtype=None,
                   text=None, content=None, metadata=None):

    return {
        "element_id": element_id,
        "order": order,
        "type": element_type,
        "subtype": subtype,
        "text": text,
        "content": content,
        "classification": None,
        "source": {
            "extraction_method": "manual_test",
            "is_ocr": False
        },
        "position": None,
        "metadata": metadata or {}
    }


test_cases = [
    {
        "name": "CODE",
        "element": create_element(
            "slide_21_element_2",
            2,
            "text",
            "code",
            "<!DOCTYPE html>\n<html></html>"
        )
    },
    {
        "name": "IMAGE",
        "element": create_element(
            "slide_18_image_1",
            10,
            "image",
            "illustration",
            metadata={
                "filename": "slide_18_image_01.png",
                "content_type": "image/png",
                "width": 81,
                "height": 65,
                "size_bytes": 5000,
                "shape_name": "Picture 1"
            }
        )
    },
    {
        "name": "TABLE",
        "element": create_element(
            "page_8_table_1",
            4,
            "table",
            "table_candidate",
            content={
                "headers": ["g", "g*g", "x/g", "(g+x/g)/2"],
                "rows": [["3", "9", "16/3", "4.17"]],
                "reconstructed": True
            }
        )
    },
    {
        "name": "DIAGRAM",
        "element": create_element(
            "page_18_diagram_1",
            2,
            "diagram",
            "diagram_content_candidate",
            content={
                "description": "Memory and control unit diagram"
            }
        )
    }
]

for case in test_cases:
    data = {
        "schema_version": "0.1",
        "document": {
            "document_id": "complex_test",
            "filename": "test.pdf",
            "format": "pdf",
            "number_of_units": 1
        },
        "units": [
            {
                "unit_id": "unit_1",
                "unit_number": 1,
                "unit_type": "page",
                "elements": [case["element"]]
            }
        ]
    }

    errors = list(validator.iter_errors(data))

    if errors:
        print(f"\n{case['name']}: INVALID")
        for error in errors:
            print("-", error.message)
    else:
        print(f"\n{case['name']}: VALID")


# Test relations
relation_data = {
    "schema_version": "0.1",
    "document": {
        "document_id": "diagram_test",
        "filename": "test.pptx",
        "format": "pptx",
        "number_of_units": 1
    },
    "units": [
        {
            "unit_id": "slide_5",
            "unit_number": 5,
            "unit_type": "slide",
            "elements": [
                create_element("element_1", 1, "text", "label", "Client browser"),
                create_element("element_2", 2, "text", "label", "Web server")
            ],
            "relations": [
                {
                    "relation_id": "relation_1",
                    "type": "connected_to",
                    "source_element_ids": ["element_1"],
                    "target_element_ids": ["element_2"],
                    "description": "Client sends a request to the server."
                }
            ]
        }
    ]
}

relation_errors = list(validator.iter_errors(relation_data))

print("\nRELATIONS:", "INVALID" if relation_errors else "VALID")

for error in relation_errors:
    print("-", error.message)

print("\n" + "=" * 55)
print("TEST FINISHED")
print("=" * 55)
