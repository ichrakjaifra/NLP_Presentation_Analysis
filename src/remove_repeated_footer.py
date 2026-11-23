
from pathlib import Path
import json


# 1. Get the project directory
project_root = Path(__file__).resolve().parent.parent

# 2. Define input and output paths
input_path = project_root / "data" / "output" / "structured_pages.json"
output_path = project_root / "data" / "output" / "structured_pages_cleaned.json"

# 3. Define the repeated footer to remove
footer_to_remove = "6.100L Lecture 1"

# 4. Check if the input file exists
if not input_path.exists():
    print("Error: Structured JSON file not found!")
    print("Expected file location:", input_path)

else:
    # 5. Read the original structured document
    with input_path.open("r", encoding="utf-8") as input_file:
        document = json.load(input_file)

    removed_count = 0

    # 6. Process each page
    for page in document["pages"]:

        lines = page["content"].splitlines()
        filtered_lines = []

        for line in lines:

            if line.strip() == footer_to_remove:
                removed_count += 1
            else:
                filtered_lines.append(line)

        # Rebuild the page content
        page["content"] = "\n".join(filtered_lines)

    # 7. Add processing information
    document["processing"] = {
        "removed_element": footer_to_remove,
        "removed_occurrences": removed_count
    }

    # 8. Save the new JSON file
    with output_path.open("w", encoding="utf-8") as output_file:
        json.dump(
            document,
            output_file,
            ensure_ascii=False,
            indent=4
        )

    # 9. Display the results
    print("Repeated footer removal completed successfully!")
    print("Number of pages:", document["number_of_pages"])
    print("Removed occurrences:", removed_count)
    print("Cleaned JSON saved to:", output_path)
