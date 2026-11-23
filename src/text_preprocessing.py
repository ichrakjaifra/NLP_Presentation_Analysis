
from pathlib import Path


# 1. Get the project directory
project_root = Path(__file__).resolve().parent.parent

# 2. Define input and output paths
input_path = project_root / "data" / "output" / "extracted_text.txt"
output_path = project_root / "data" / "output" / "cleaned_text.txt"


# 3. Check if the extracted text file exists
if not input_path.exists():
    print("Error: Extracted text file not found!")
    print("Expected file location:", input_path)

else:
    # 4. Read the extracted text
    with input_path.open("r", encoding="utf-8") as input_file:
        raw_text = input_file.read()

    # 5. Prepare the cleaned text
    cleaned_lines = []
    previous_line_was_empty = False

    # 6. Process the text line by line
    for line in raw_text.splitlines():

        # Remove unnecessary spaces at the beginning and end
        line = line.strip()

        # Replace the original bullet symbol with a standard bullet
        line = line.replace("", "- ")

        # Keep only one empty line between text blocks
        if line == "":
            if not previous_line_was_empty:
                cleaned_lines.append("")
            previous_line_was_empty = True

        else:
            cleaned_lines.append(line)
            previous_line_was_empty = False

    # 7. Rebuild the cleaned text
    cleaned_text = "\n".join(cleaned_lines)

    # 8. Create the output directory if necessary
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # 9. Save the cleaned text into a new TXT file
    with output_path.open("w", encoding="utf-8") as output_file:
        output_file.write(cleaned_text)

    # 10. Display the results
    print("Text preprocessing completed successfully!")
    print("Cleaned text saved to:", output_path)
