
import json
import re
from pathlib import Path


# ============================================================
# 1. Project paths
# ============================================================

project_root = Path(__file__).resolve().parent.parent

input_file = (
    project_root
    / "data"
    / "output"
    / "pptx_extracted_text_cleaned.json"
)

output_file = (
    project_root
    / "data"
    / "output"
    / "pptx_classified_text.json"
)


# ============================================================
# 2. Load cleaned PowerPoint text
# ============================================================

with open(input_file, "r", encoding="utf-8") as file:
    slides = json.load(file)


# ============================================================
# 3. Detect programming code
# ============================================================

def is_code(text):
    """
    Detect actual programming code blocks.

    Complete HTML documents and JavaScript code structures
    are detected.

    Explanatory paragraphs containing inline HTML tags
    are not classified as code.
    """

    stripped_text = text.strip()

    lines = [
        line.strip()
        for line in stripped_text.splitlines()
        if line.strip()
    ]

    if not lines:
        return False

    # Check whether the text starts with an HTML document
    first_line = lines[0]

    html_document_start = bool(
        re.match(
            r"^(<!DOCTYPE\s+html|<html\b)",
            first_line,
            re.IGNORECASE
        )
    )

    html_patterns = [
        r"<!DOCTYPE\s+html",
        r"<html[\s>]",
        r"<head[\s>]",
        r"<body[\s>]",
        r"</html>",
    ]

    html_score = sum(
        bool(re.search(pattern, stripped_text, re.IGNORECASE))
        for pattern in html_patterns
    )

    if html_document_start and html_score >= 3:
        return True

    # Detect JavaScript code structures
    javascript_patterns = [
        r"\bfunction\s+\w+\s*\(",
        r"\bconst\s+\w+\s*=",
        r"\blet\s+\w+\s*=",
        r"\bvar\s+\w+\s*=",
        r"document\.getElementById",
        r"console\.log\s*\(",
    ]

    javascript_score = sum(
        bool(re.search(pattern, stripped_text))
        for pattern in javascript_patterns
    )

    if javascript_score >= 2:
        return True

    # Detect a JavaScript comment block combined with a function
    if (
        re.search(r"/\*.*?\*/", stripped_text, re.DOTALL)
        and re.search(r"\bfunction\s+\w+\s*\(", stripped_text)
    ):
        return True

    return False


# ============================================================
# 4. Detect presentation metadata
# ============================================================

def is_metadata(text):
    """
    Detect presentation metadata such as dates and source credits.
    """

    metadata_patterns = [
        r"slides?\s+courtesy\s+of",
        r"presented\s+by",
        r"instructor\s*:",
        r"professor\s*:",
        r"lecturer\s*:",
        r"course\s*:",
        r"date\s*:",
        r"university\s*:",
    ]

    date_pattern = (
        r"\b(?:January|February|March|April|May|June|July|August|"
        r"September|October|November|December)\s+"
        r"\d{1,2},?\s+\d{4}\b"
    )

    if re.search(date_pattern, text, re.IGNORECASE):
        return True

    return any(
        re.search(pattern, text, re.IGNORECASE)
        for pattern in metadata_patterns
    )


# ============================================================
# 5. Detect numbered or bulleted lists
# ============================================================

def is_numbered_list(text):
    """
    Detect numbered or bulleted list elements.
    """

    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    if not lines:
        return False

    numbered_pattern = r"^\s*(?:\d+[\.\)]|[-•*])\s+"

    matching_lines = sum(
        bool(re.match(numbered_pattern, line))
        for line in lines
    )

    return matching_lines >= 1


# ============================================================
# 6. Main classification function
# ============================================================

def classify_text(text, element_index, slide_title=""):
    """
    Assign a heuristic category to one extracted text element.
    """

    text = text.strip()

    if not text:
        return "other_candidate", "Empty text element"

    # 1. Text without meaningful alphanumeric content
    if not re.search(r"[a-zA-Z0-9]", text):
        return "other_candidate", "No meaningful alphanumeric content"

    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    # 2. First element of each slide
    if element_index == 0:
        return "title_candidate", "First text element of the slide"

    # 3. Presentation metadata
    if is_metadata(text):
        return "metadata_candidate", "Presentation metadata detected"

    # 4. Actual programming code blocks
    if is_code(text):
        return "code_candidate", "Programming code structure detected"

    # 5. Grading descriptions
    grading_keywords = [
        "grading scale",
        "grading criteria",
        "evaluation criteria",
        "assessment criteria",
    ]

    title_lower = slide_title.lower()

    if any(keyword in title_lower for keyword in grading_keywords):
        if element_index >= 2 and len(text) > 20:
            return (
                "description_candidate",
                "Description associated with grading criteria"
            )

    # 6. Numbered or bulleted lists
    if is_numbered_list(text):
        return "list_candidate", "Numbered or bulleted list detected"

    # 7. Explanatory paragraphs containing multiple sentences
    sentence_lines = sum(
        1
        for line in lines
        if re.search(r"[.!?]\s*$", line)
    )

    if len(lines) >= 2 and sentence_lines >= 2:
        return (
            "paragraph_candidate",
            "Multiple complete explanatory sentences detected"
        )

    # 8. Multiple short lines
    if len(lines) >= 2:

        average_line_length = sum(
            len(line) for line in lines
        ) / len(lines)

        if average_line_length <= 65:
            return (
                "list_candidate",
                "Multiple short lines detected"
            )

    # 9. Short labels
    if len(text) <= 60 and not re.search(r"[.!?]$", text):
        return "label_candidate", "Short text without sentence punctuation"

    # 10. Default category
    return "paragraph_candidate", "General explanatory text"


# ============================================================
# 7. Classify all slides
# ============================================================

classified_slides = []

category_counts = {}

total_elements = 0

for slide in slides:

    slide_number = slide["slide_number"]
    content = slide["content"]

    classified_content = []

    slide_title = content[0] if content else ""

    for element_index, text in enumerate(content):

        category, reason = classify_text(
            text,
            element_index,
            slide_title
        )

        classified_element = {
            "element_id": element_index + 1,
            "text": text,
            "category": category,
            "reason": reason
        }

        classified_content.append(classified_element)

        category_counts[category] = (
            category_counts.get(category, 0) + 1
        )

        total_elements += 1

    classified_slides.append({
        "slide_number": slide_number,
        "content": classified_content
    })


# ============================================================
# 8. Save classified JSON
# ============================================================

output_file.parent.mkdir(parents=True, exist_ok=True)

with open(output_file, "w", encoding="utf-8") as file:
    json.dump(
        classified_slides,
        file,
        ensure_ascii=False,
        indent=4
    )


# ============================================================
# 9. Display classification summary
# ============================================================

print("========== POWERPOINT TEXT CLASSIFICATION ==========")

print("Total slides:", len(classified_slides))
print("Total text elements:", total_elements)

print("\n========== CATEGORY DISTRIBUTION ==========")

for category, count in sorted(category_counts.items()):
    print(f"{category}: {count}")

print("\n========== OUTPUT ==========")
print("Classified JSON:", output_file)

print("\nClassification completed successfully.")
