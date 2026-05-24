"""Detection and repair of special/control character issues in CSV fields."""

import re
import unicodedata
from typing import List, Tuple

# Control characters (except common whitespace like \t, \n, \r)
CONTROL_CHAR_RE = re.compile(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]')

# Zero-width and invisible Unicode characters
INVISIBLE_CHAR_RE = re.compile(
    r'[\u200b\u200c\u200d\u200e\u200f\ufeff\u00ad]'
)


def find_control_chars(field: str) -> List[str]:
    """Return list of control characters found in a field."""
    return CONTROL_CHAR_RE.findall(field)


def find_invisible_chars(field: str) -> List[str]:
    """Return list of invisible/zero-width characters found in a field."""
    return INVISIBLE_CHAR_RE.findall(field)


def strip_special_chars(field: str, replacement: str = "") -> str:
    """Remove control and invisible characters from a field."""
    field = CONTROL_CHAR_RE.sub(replacement, field)
    field = INVISIBLE_CHAR_RE.sub(replacement, field)
    return field


def fix_special_chars_in_row(row: List[str]) -> Tuple[List[str], int]:
    """Strip special characters from all fields in a row.

    Returns the cleaned row and the number of fields that were modified.
    """
    fixed = []
    count = 0
    for field in row:
        cleaned = strip_special_chars(field)
        if cleaned != field:
            count += 1
        fixed.append(cleaned)
    return fixed, count


def find_specialchar_issues(rows: List[List[str]]) -> List[dict]:
    """Scan all rows and report fields containing special characters."""
    issues = []
    for row_idx, row in enumerate(rows):
        for col_idx, field in enumerate(row):
            ctrl = find_control_chars(field)
            invis = find_invisible_chars(field)
            if ctrl or invis:
                issues.append({
                    "row": row_idx,
                    "col": col_idx,
                    "field": field,
                    "control_chars": ctrl,
                    "invisible_chars": invis,
                })
    return issues


def fix_specialchars_in_content(
    rows: List[List[str]]
) -> Tuple[List[List[str]], int]:
    """Fix special characters across all rows.

    Returns cleaned rows and total number of fixed fields.
    """
    fixed_rows = []
    total = 0
    for row in rows:
        fixed_row, count = fix_special_chars_in_row(row)
        total += count
        fixed_rows.append(fixed_row)
    return fixed_rows, total
