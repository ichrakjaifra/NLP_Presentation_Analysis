
import json
from pathlib import Path
from jsonschema import Draft202012Validator

project_root = Path(__file__).resolve().parent.parent

schema_file = project_root / "schema" / "unified_schema_v0_1.json"

print("========== UNIFIED JSON SCHEMA TEST ==========")

with open(schema_file, "r", encoding="utf-8") as file:
    schema = json.load(file)

Draft202012Validator.check_schema(schema)

print("Schema JSON syntax: VALID")
print("Schema structure: VALID")
print("Schema version:", schema["properties"]["schema_version"]["const"])
print("Schema file:", schema_file.name)

print("\nSchema is ready for data validation.")
