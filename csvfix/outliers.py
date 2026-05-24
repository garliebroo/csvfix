"""Detect numeric outliers in CSV columns using IQR-based method."""

import csv
import io
from typing import Optional


def get_numeric_values(column: list[str]) -> list[float]:
    """Extract numeric values from a column, skipping non-numeric entries."""
    values = []
    for val in column:
        try:
            values.append(float(val.strip()))
        except (ValueError, AttributeError):
            pass
    return values


def compute_iqr_bounds(values: list[float], multiplier: float = 1.5) -> tuple[float, float]:
    """Compute lower and upper IQR-based outlier bounds."""
    if len(values) < 4:
        return (float("-inf"), float("inf"))
    sorted_vals = sorted(values)
    n = len(sorted_vals)
    q1 = sorted_vals[n // 4]
    q3 = sorted_vals[(3 * n) // 4]
    iqr = q3 - q1
    return (q1 - multiplier * iqr, q3 + multiplier * iqr)


def find_outliers_in_column(
    column: list[str], multiplier: float = 1.5
) -> list[tuple[int, str]]:
    """Return list of (index, value) pairs that are outliers in the column."""
    numeric = get_numeric_values(column)
    lower, upper = compute_iqr_bounds(numeric, multiplier)
    outliers = []
    for i, val in enumerate(column):
        try:
            fval = float(val.strip())
            if fval < lower or fval > upper:
                outliers.append((i, val))
        except (ValueError, AttributeError):
            pass
    return outliers


def find_outlier_issues(
    content: str, multiplier: float = 1.5, has_header: bool = True
) -> list[dict]:
    """Scan CSV content and report outlier values per column."""
    reader = csv.reader(io.StringIO(content))
    rows = list(reader)
    if not rows:
        return []

    start = 1 if has_header else 0
    headers = rows[0] if has_header else [str(i) for i in range(len(rows[0]))]
    data_rows = rows[start:]

    if not data_rows:
        return []

    num_cols = len(headers)
    issues = []

    for col_idx in range(num_cols):
        column = [row[col_idx] if col_idx < len(row) else "" for row in data_rows]
        outliers = find_outliers_in_column(column, multiplier)
        for row_offset, val in outliers:
            actual_row = start + row_offset
            issues.append({
                "row": actual_row,
                "col": col_idx,
                "col_name": headers[col_idx],
                "value": val,
                "issue": "numeric_outlier",
            })

    return issues
