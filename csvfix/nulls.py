"""Detection and repair of null/empty value issues in CSV files."""

import csv
import io
from typing import List, Tuple, Dict, Optional


NULL_STRINGS = {"null", "none", "na", "n/a", "nil", "#n/a", "-"}


def is_null_like(value: str, custom_nulls: Optional[List[str]] = None) -> bool:
    """Return True if the value looks like a null placeholder."""
    check = value.strip().lower()
    if check == "":
        return True
    nulls = NULL_STRINGS.copy()
    if custom_nulls:
        nulls.update(s.lower() for s in custom_nulls)
    return check in nulls


def normalize_null(value: str, replacement: str = "", custom_nulls: Optional[List[str]] = None) -> str:
    """Replace null-like values with a canonical replacement (default: empty string)."""
    if is_null_like(value, custom_nulls):
        return replacement
    return value


def fix_nulls_in_row(
    row: List[str],
    replacement: str = "",
    custom_nulls: Optional[List[str]] = None,
) -> Tuple[List[str], int]:
    """Fix null-like values in a single row. Returns (fixed_row, count_changed)."""
    fixed = []
    changed = 0
    for field in row:
        normalized = normalize_null(field, replacement, custom_nulls)
        if normalized != field:
            changed += 1
        fixed.append(normalized)
    return fixed, changed


def find_null_issues(content: str, custom_nulls: Optional[List[str]] = None) -> List[Dict]:
    """Scan CSV content and report rows/fields with null-like values."""
    issues = []
    reader = csv.reader(io.StringIO(content))
    for row_idx, row in enumerate(reader):
        for col_idx, field in enumerate(row):
            if is_null_like(field, custom_nulls):
                issues.append({
                    "row": row_idx,
                    "col": col_idx,
                    "value": repr(field),
                })
    return issues


def fix_nulls_in_content(
    content: str,
    replacement: str = "",
    custom_nulls: Optional[List[str]] = None,
) -> Tuple[str, int]:
    """Fix all null-like values in CSV content. Returns (fixed_content, total_changes)."""
    reader = csv.reader(io.StringIO(content))
    output = io.StringIO()
    writer = csv.writer(output, lineterminator="\n")
    total = 0
    for row in reader:
        fixed_row, count = fix_nulls_in_row(row, replacement, custom_nulls)
        total += count
        writer.writerow(fixed_row)
    return output.getvalue(), total
