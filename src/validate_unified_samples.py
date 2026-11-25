
import json
from pathlib import Path
from jsonschema import Draft202012Validator

# Project paths
project_root = Path(__file__).resolve().parent.parent

schema_file = project_root / "schema" / "unified_schema_v0_1.json"
samples_folder = project_root / "data" / "output" / "unified"

sample_files = [
    samples_folder / "sample_pdf_page_1.json",
    samples_folder / "sample_pptx_slide_1.json"
]

print("========== UNIFIED DATA VALIDATION ==========")

# Load and check schema
with open(schema_file, "r", encoding="utf-8") as file:
    schema = json.load(file)

Draft202012Validator.check_schema(schema)
validator = Draft202012Validator(schema)

print("\nSchema loaded successfully.")

# Validate samples
for sample_file in sample_files:
    print(f"\nTesting: {sample_file.name}")

    with open(sample_file, "r", encoding="utf-8") as file:
        data = json.load(file)

    errors = sorted(
        validator.iter_errors(data),
        key=lambda error: list(error.absolute_path)
    )

    if not errors:
        print("Result: VALID")
        print("Format:", data["document"]["format"])
        print("Units tested:", len(data["units"]))
    else:
        print("Result: INVALID")
        for error in errors:
            location = " -> ".join(
                str(part) for part in error.absolute_path
            )
            print(f"- Location: {location}")
            print(f"  Error: {error.message}")

print("\n========== VALIDATION FINISHED ==========")
