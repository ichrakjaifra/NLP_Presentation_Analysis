
import json
import re
from pathlib import Path


# ==================================================
# 1. PROJECT PATHS
# ==================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

INPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "output"
    / "pdf_text_blocks_cleaned.json"
)

OUTPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "output"
    / "classified_text_blocks_v2.json"
)


# ==================================================
# 2. DIAGRAM LABELS
# ==================================================

DIAGRAM_LABELS = {
    "MEMORY",
    "CONTROL",
    "UNIT",
    "ARITHMETIC LOGIC UNIT",
    "INPUT",
    "OUTPUT",
    "ALU",
    "PROCESSOR",
    "CPU"
}


# ==================================================
# 3. GENERAL HELPER FUNCTIONS
# ==================================================

def get_block_text(block):
    """
    Extract text from a block.
    """

    return str(
        block.get("content", block.get("text", ""))
    ).strip()


def get_bbox(block):
    """
    Read bounding box coordinates.

    Supports:
    - Dictionary: {"x0": ..., "y0": ..., "x1": ..., "y1": ...}
    - List: [x0, y0, x1, y1]
    """

    bbox = block.get("bbox")

    # Dictionary format
    if isinstance(bbox, dict):

        try:
            return [
                float(bbox["x0"]),
                float(bbox["y0"]),
                float(bbox["x1"]),
                float(bbox["y1"])
            ]

        except (KeyError, TypeError, ValueError):
            return None

    # List or tuple format
    if isinstance(bbox, (list, tuple)) and len(bbox) == 4:

        try:
            return [float(value) for value in bbox]

        except (TypeError, ValueError):
            return None

    return None


def normalize_text(text):
    """
    Normalize text for comparison.
    """

    text = text.upper()
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def get_lines(text):
    """
    Return non-empty lines.
    """

    return [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]


# ==================================================
# 4. DIAGRAM DETECTION
# ==================================================

def is_diagram_label(text):
    """
    Detect one or several diagram labels
    inside the same text block.
    """

    normalized = normalize_text(text)

    lines = {
        normalize_text(line)
        for line in get_lines(text)
    }

    if normalized in DIAGRAM_LABELS:
        return True

    if lines and lines.issubset(DIAGRAM_LABELS):
        return True

    return False


def is_diagram_page(blocks):
    """
    Detect whether a page contains several
    known diagram labels.
    """

    detected_labels = set()

    for block in blocks:

        text = get_block_text(block)

        for line in get_lines(text):

            normalized = normalize_text(line)

            if normalized in DIAGRAM_LABELS:
                detected_labels.add(normalized)

    # At least three different labels
    # are required to identify a diagram-rich page.
    return len(detected_labels) >= 3


# ==================================================
# 5. LIST DETECTION
# ==================================================

def is_list_candidate(text):
    """
    Detect bullet lists and numbered steps.

    Simple numeric values such as 3, 9 or 4.17
    are not considered list markers.
    """

    lines = get_lines(text)

    for line in lines:

        # Bullet markers
        if re.match(r"^\s*(?:|[-*•])\s*", line):
            return True

        # Numbered markers such as:
        # 1) or 2.
        if re.match(r"^\s*\d+[\.)]\s*$", line):
            return True

        # Numbered steps followed by text
        if re.match(r"^\s*\d+[\.)]\s+\S+", line):
            return True

    return False


# ==================================================
# 6. NUMERIC VALUE DETECTION
# ==================================================

def is_numeric_value_line(line):
    """
    Detect numeric values, fractions and Boolean values.
    """

    line = line.strip()

    pattern = (
        r"^(?:"
        r"-?\d+(?:\.\d+)?"
        r"|"
        r"-?\d+/\d+"
        r"|"
        r"TRUE"
        r"|"
        r"FALSE"
        r")$"
    )

    return bool(
        re.fullmatch(pattern, line, flags=re.IGNORECASE)
    )


def is_numeric_block(text):
    """
    Check whether all lines in a block are numeric values.
    """

    lines = get_lines(text)

    if len(lines) < 2:
        return False

    return all(
        is_numeric_value_line(line)
        for line in lines
    )


# ==================================================
# 7. TABLE DETECTION
# ==================================================

def is_table_pair(block_a, block_b):
    """
    Detect two vertically adjacent blocks
    that may represent table headings and values.
    """

    text_a = get_block_text(block_a)
    text_b = get_block_text(block_b)

    lines_a = get_lines(text_a)
    lines_b = get_lines(text_b)

    # Each block must contain at least 3 lines.
    if len(lines_a) < 3 or len(lines_b) < 3:
        return False

    a_is_numeric = is_numeric_block(text_a)
    b_is_numeric = is_numeric_block(text_b)

    # Exactly one block should contain numeric values.
    if a_is_numeric == b_is_numeric:
        return False

    # Read bounding boxes.
    bbox_a = get_bbox(block_a)
    bbox_b = get_bbox(block_b)

    if bbox_a is None or bbox_b is None:
        return False

    x0_a, y0_a, x1_a, y1_a = bbox_a
    x0_b, y0_b, x1_b, y1_b = bbox_b

    # Compare horizontal alignment.
    x_difference = abs(x0_a - x0_b)

    if x_difference > 25:
        return False

    # Calculate vertical distance.
    vertical_gap = max(y0_a, y0_b) - min(y1_a, y1_b)

    # Blocks must be close vertically.
    if vertical_gap > 12:
        return False

    return True


def detect_table_blocks(blocks):
    """
    Identify blocks belonging to possible tables.
    """

    table_block_ids = set()

    for index in range(len(blocks) - 1):

        current_block = blocks[index]
        next_block = blocks[index + 1]

        if is_table_pair(current_block, next_block):

            table_block_ids.add(id(current_block))
            table_block_ids.add(id(next_block))

    return table_block_ids


# ==================================================
# 8. TITLE DETECTION
# ==================================================

def is_title_candidate(text):
    """
    Detect short text written in uppercase
    in its original form.
    """

    text = text.strip()

    return (
        len(text) <= 60
        and text == text.upper()
        and any(char.isalpha() for char in text)
    )


# ==================================================
# 9. BLOCK CLASSIFICATION
# ==================================================

def classify_block(block, diagram_page, table_block_ids):

    text = get_block_text(block)

    if not text:

        return (
            "empty_candidate",
            "The block contains no text."
        )

    # Rule 1: Diagram labels.
    if diagram_page and is_diagram_label(text):

        return (
            "diagram_label_candidate",
            "The block contains one or several known diagram labels."
        )

    # Rule 2: Possible table blocks.
    if id(block) in table_block_ids:

        return (
            "table_candidate",
            "The block is aligned with an adjacent heading/value block."
        )

    # Rule 3: Diagram content.
    if diagram_page:

        return (
            "diagram_content_candidate",
            "The block belongs to a page containing several diagram labels."
        )

    # Rule 4: Lists and numbered steps.
    if is_list_candidate(text):

        return (
            "list_candidate",
            "The block contains bullet markers or numbered steps."
        )

    # Rule 5: Uppercase titles.
    if is_title_candidate(text):

        return (
            "title_or_label_candidate",
            "The original block contains short uppercase text."
        )

    # Rule 6: Short labels.
    lines = get_lines(text)

    if len(text) <= 30 and len(lines) <= 2:

        return (
            "short_label_candidate",
            "The block contains a short text."
        )

    # Rule 7: Default classification.
    return (
        "paragraph_candidate",
        "The block does not match the previous rules."
    )


# ==================================================
# 10. MAIN PROCESSING FUNCTION
# ==================================================


def main():

    # 1. Load input JSON
    with open(INPUT_FILE, "r", encoding="utf-8") as file:
        data = json.load(file)

    # 2. Retrieve pages from JSON
    if isinstance(data, dict):
        if "pages" not in data:
            raise ValueError(
                "The input JSON does not contain a 'pages' key. "
                f"Available keys: {list(data.keys())}"
            )

        pages = data["pages"]

    elif isinstance(data, list):
        pages = data

    else:
        raise ValueError("Unexpected JSON structure.")

    # Verify pages structure
    if not isinstance(pages, list):
        raise ValueError("'pages' must contain a list of pages.")

    # 3. Initialize counters
    total_blocks = 0
    classification_counts = {}

    # 4. Classify blocks page by page
    for page in pages:

        if not isinstance(page, dict):
            continue

        blocks = page.get("blocks", [])

        if not isinstance(blocks, list):
            continue

        # Detect diagram-rich page
        diagram_page = is_diagram_page(blocks)

        # Detect possible table blocks
        table_block_ids = detect_table_blocks(blocks)

        for block in blocks:

            total_blocks += 1

            # Apply V2 classification rules
            predicted_type, reason = classify_block(
                block,
                diagram_page,
                table_block_ids
            )

            block["predicted_type"] = predicted_type
            block["classification_reason"] = reason

            # Count classifications
            classification_counts[predicted_type] = (
                classification_counts.get(predicted_type, 0) + 1
            )

    # 5. Save classified results
    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

    # 6. Display general results
    print("Text block classification V2 completed successfully!")
    print("Number of pages:", len(pages))
    print("Number of classified blocks:", total_blocks)

    print("\nClassification results:")

    for label, count in sorted(classification_counts.items()):
        print(f"{label}: {count}")

    # 7. Audit all detected table candidates
    print("\n========== TABLE CANDIDATES AUDIT ==========")

    table_candidate_count = 0

    for page in pages:

        if not isinstance(page, dict):
            continue

        page_number = page.get("page_number")

        for block in page.get("blocks", []):

            if block.get("predicted_type") == "table_candidate":

                table_candidate_count += 1

                print(f"\nPage: {page_number}")
                print("Block ID:", block.get("block_id"))
                print("Content:")
                print(get_block_text(block))
                print("Reason:", block.get("classification_reason"))

    print("\nTotal table candidate blocks:", table_candidate_count)

    # 8. Display output location
    print("\nOutput saved to:", OUTPUT_FILE)


if __name__ == "__main__":
    main()

