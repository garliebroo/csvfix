import csv
from io import StringIO
from typing import Optional


def is_in_range(
    value: str,
    min_val: Optional[float] = None,
    max_val: Optional[float] = None,
) -> bool:
    """Return True if value parses as a number and falls within [min_val, max_val]."""
    try:
        num = float(value)
    except (ValueError, TypeError):
        return True  # non-numeric values are not checked
    if min_val is not None and num < min_val:
        return False
    if max_val is not None and num > max_val:
        return False
    return True


def find_out_of_range_fields(
    rows: list[list[str]],
    column_index: int,
    min_val: Optional[float] = None,
    max_val: Optional[float] = None,
    has_header: bool = True,
) -> list[dict]:
    """Find fields in a column that fall outside the given numeric range."""
    issues = []
    start = 1 if has_header else 0
    for row_idx in range(start, len(rows)):
        row = rows[row_idx]
        if column_index >= len(row):
            continue
        value = row[column_index]
        if not is_in_range(value, min_val, max_val):
            issues.append({
                "row": row_idx,
                "column": column_index,
                "value": value,
                "min": min_val,
                "max": max_val,
            })
    return issues


def find_rangecheck_issues(
    content: str,
    column_ranges: dict[int, tuple[Optional[float], Optional[float]]],
    has_header: bool = True,
) -> list[dict]:
    """Scan CSV content for out-of-range numeric values.

    column_ranges maps column index -> (min_val, max_val).
    Pass None for either bound to skip that side of the check.
    """
    reader = csv.reader(StringIO(content))
    rows = list(reader)
    issues = []
    for col_idx, (min_val, max_val) in column_ranges.items():
        issues.extend(
            find_out_of_range_fields(rows, col_idx, min_val, max_val, has_header)
        )
    return issues
