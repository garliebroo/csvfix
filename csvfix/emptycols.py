"""Detect and remove empty columns from CSV content."""

import csv
import io
from typing import List, Tuple, Dict


def find_empty_columns(rows: List[List[str]]) -> List[int]:
    """Return indices of columns that are empty (or null-like) in every row."""
    if not rows:
        return []

    num_cols = max(len(row) for row in rows)
    empty_indices = []

    for col_idx in range(num_cols):
        all_empty = all(
            col_idx >= len(row) or row[col_idx].strip() == ""
            for row in rows
        )
        if all_empty:
            empty_indices.append(col_idx)

    return empty_indices


def remove_empty_columns(rows: List[List[str]], empty_indices: List[int]) -> List[List[str]]:
    """Return rows with the specified column indices removed."""
    if not empty_indices:
        return rows
    index_set = set(empty_indices)
    return [
        [field for i, field in enumerate(row) if i not in index_set]
        for row in rows
    ]


def find_empty_column_issues(rows: List[List[str]]) -> Dict:
    """Return a report dict describing empty column findings."""
    empty_indices = find_empty_columns(rows)
    return {
        "empty_column_indices": empty_indices,
        "empty_column_count": len(empty_indices),
    }


def fix_empty_columns_in_content(content: str, delimiter: str = ",") -> Tuple[str, int]:
    """Strip fully-empty columns from CSV content string.

    Returns (fixed_content, number_of_columns_removed).
    """
    reader = csv.reader(io.StringIO(content), delimiter=delimiter)
    rows = list(reader)

    if not rows:
        return content, 0

    empty_indices = find_empty_columns(rows)
    if not empty_indices:
        return content, 0

    cleaned_rows = remove_empty_columns(rows, empty_indices)

    out = io.StringIO()
    writer = csv.writer(out, delimiter=delimiter, lineterminator="\n")
    writer.writerows(cleaned_rows)
    return out.getvalue(), len(empty_indices)
