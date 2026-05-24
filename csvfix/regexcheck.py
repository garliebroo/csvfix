import re
import csv
from io import StringIO
from typing import Optional


def is_valid_pattern(value: str, pattern: str) -> bool:
    """Return True if value fully matches the given regex pattern."""
    try:
        return bool(re.fullmatch(pattern, value))
    except re.error:
        return False


def looks_like_pattern_column(values: list[str], pattern: str, threshold: float = 0.7) -> bool:
    """Heuristic: does a column look like it should match pattern?"""
    non_empty = [v for v in values if v.strip()]
    if not non_empty:
        return False
    matches = sum(1 for v in non_empty if is_valid_pattern(v, pattern))
    return (matches / len(non_empty)) >= threshold


def find_invalid_pattern_fields(
    rows: list[list[str]],
    col_index: int,
    pattern: str,
    skip_empty: bool = True,
) -> list[dict]:
    """Find fields in a column that do not match the given regex pattern."""
    issues = []
    for row_idx, row in enumerate(rows):
        if col_index >= len(row):
            continue
        value = row[col_index]
        if skip_empty and not value.strip():
            continue
        if not is_valid_pattern(value, pattern):
            issues.append({
                "row": row_idx,
                "col": col_index,
                "value": value,
                "pattern": pattern,
            })
    return issues


def find_regexcheck_issues(
    content: str,
    column_patterns: dict[int, str],
    has_header: bool = True,
) -> list[dict]:
    """Scan CSV content for fields failing column-specific regex patterns.

    Args:
        content: Raw CSV text.
        column_patterns: Mapping of column index -> regex pattern string.
        has_header: Whether the first row is a header (skipped from checks).

    Returns:
        List of issue dicts with row, col, value, and pattern keys.
    """
    reader = csv.reader(StringIO(content))
    rows = list(reader)
    if not rows:
        return []

    data_rows = rows[1:] if has_header else rows
    offset = 1 if has_header else 0

    issues = []
    for col_index, pattern in column_patterns.items():
        col_issues = find_invalid_pattern_fields(data_rows, col_index, pattern)
        for issue in col_issues:
            issue["row"] += offset
        issues.extend(col_issues)

    return issues
