"""Detect and fix whitespace issues in CSV fields."""

import csv
import io
import re


def strip_field_whitespace(row: list[str]) -> list[str]:
    """Strip leading/trailing whitespace from each field in a row."""
    return [field.strip() for field in row]


def collapse_internal_whitespace(value: str) -> str:
    """Replace runs of internal whitespace with a single space."""
    return re.sub(r"[ \t]+", " ", value).strip()


def fix_whitespace_in_content(
    content: str,
    delimiter: str = ",",
    strip: bool = True,
    collapse: bool = False,
) -> str:
    """Apply whitespace fixes to all fields in CSV content.

    Args:
        content: Raw CSV string.
        delimiter: Field delimiter to use.
        strip: Strip leading/trailing whitespace from fields.
        collapse: Collapse internal whitespace runs to single space.

    Returns:
        Fixed CSV string.
    """
    reader = csv.reader(io.StringIO(content), delimiter=delimiter)
    output = io.StringIO()
    writer = csv.writer(output, delimiter=delimiter, lineterminator="\n")

    for row in reader:
        fixed = row
        if strip:
            fixed = strip_field_whitespace(fixed)
        if collapse:
            fixed = [collapse_internal_whitespace(f) for f in fixed]
        writer.writerow(fixed)

    return output.getvalue()


def find_whitespace_issues(content: str, delimiter: str = ",") -> list[dict]:
    """Scan CSV content and report fields with whitespace problems.

    Returns a list of dicts with row, col, and the offending value.
    """
    issues = []
    reader = csv.reader(io.StringIO(content), delimiter=delimiter)
    for row_idx, row in enumerate(reader):
        for col_idx, field in enumerate(row):
            if field != field.strip() or re.search(r"[ \t]{2,}", field):
                issues.append(
                    {"row": row_idx, "col": col_idx, "value": repr(field)}
                )
    return issues


def has_whitespace_issues(content: str, delimiter: str = ",") -> bool:
    """Return True if any field in the CSV content has whitespace problems.

    This is a fast short-circuiting alternative to find_whitespace_issues
    when you only need to know whether issues exist, not where they are.
    """
    reader = csv.reader(io.StringIO(content), delimiter=delimiter)
    for row in reader:
        for field in row:
            if field != field.strip() or re.search(r"[ \t]{2,}", field):
                return True
    return False
