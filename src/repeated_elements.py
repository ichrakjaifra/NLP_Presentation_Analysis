
from pathlib import Path
import json
from collections import Counter, defaultdict


# 1. Get the project directory
project_root = Path(__file__).resolve().parent.parent

# 2. Define input and output paths
input_path = project_root / "data" / "output" / "structured_pages.json"
output_path = project_root / "data" / "output" / "repeated_elements_report.json"


# 3. Check if the input file exists
if not input_path.exists():
    print("Error: Structured JSON file not found!")
    print("Expected file location:", input_path)

else:
    # 4. Read the structured document
    with input_path.open("r", encoding="utf-8") as input_file:
        document = json.load(input_file)

    # 5. Prepare counters
    line_counter = Counter()
    line_pages = defaultdict(list)

    # 6. Analyze the content of each page
    for page in document["pages"]:

        page_number = page["page_number"]
        content = page["content"]

        # Analyze each line separately
        for line in content.splitlines():

            line = line.strip()

            if line:
                line_counter[line] += 1
                line_pages[line].append(page_number)

    # 7. Select lines that appear more than once
    repeated_elements = []

    for line, count in line_counter.items():

        if count > 1:
            repeated_elements.append({
                "text": line,
                "occurrences": count,
                "pages": line_pages[line]
            })

    # 8. Sort results by number of occurrences
    repeated_elements.sort(
        key=lambda element: element["occurrences"],
        reverse=True
    )

    # 9. Prepare the report
    report = {
        "source_file": document["source_file"],
        "number_of_pages": document["number_of_pages"],
        "number_of_repeated_elements": len(repeated_elements),
        "repeated_elements": repeated_elements
    }

    # 10. Save the report
    with output_path.open("w", encoding="utf-8") as output_file:
        json.dump(
            report,
            output_file,
            ensure_ascii=False,
            indent=4
        )

    # 11. Display the results
    print("Repeated elements analysis completed successfully!")
    print("Number of pages:", document["number_of_pages"])
    print("Number of repeated elements:", len(repeated_elements))
    print("Report saved to:", output_path)
