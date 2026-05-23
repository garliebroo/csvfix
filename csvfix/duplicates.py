"""Detection and removal of duplicate rows in CSV files."""

import csv
import io
from collections import Counter
from typing import List, Tuple, Optional


def find_duplicate_rows(rows: List[List[str]]) -> List[int]:
    """Return indices of duplicate rows (keeping first occurrence)."""
    seen = {}
    duplicates = []
    for i, row in enumerate(rows):
        key = tuple(row)
        if key in seen:
            duplicates.append(i)
        else:
            seen[key] = i
    return duplicates


def remove_duplicate_rows(rows: List[List[str]]) -> List[List[str]]:
    """Return rows with duplicates removed, preserving first occurrence."""
    seen = set()
    result = []
    for row in rows:
        key = tuple(row)
        if key not in seen:
            seen.add(key)
            result.append(row)
    return result


def find_duplicate_keys(
    rows: List[List[str]], key_column: int
) -> List[Tuple[int, str]]:
    """Return (row_index, key_value) for rows with duplicate key column values."""
    counts: Counter = Counter()
    for row in rows:
        if key_column < len(row):
            counts[row[key_column]] += 1

    duplicates = []
    for i, row in enumerate(rows):
        if key_column < len(row) and counts[row[key_column]] > 1:
            duplicates.append((i, row[key_column]))
    return duplicates


def find_duplicate_issues(content: str) -> List[str]:
    """Analyze CSV content and return a list of human-readable duplicate issues."""
    issues = []
    reader = csv.reader(io.StringIO(content))
    rows = list(reader)
    if not rows:
        return issues

    dup_indices = find_duplicate_rows(rows)
    if dup_indices:
        issues.append(
            f"Found {len(dup_indices)} duplicate row(s) at indices: {dup_indices}"
        )
    return issues


def fix_duplicates_in_content(content: str) -> Tuple[str, int]:
    """Remove duplicate rows from CSV content. Returns (fixed_content, num_removed)."""
    reader = csv.reader(io.StringIO(content))
    rows = list(reader)
    original_count = len(rows)
    deduped = remove_duplicate_rows(rows)
    removed = original_count - len(deduped)

    output = io.StringIO()
    writer = csv.writer(output, lineterminator="\n")
    writer.writerows(deduped)
    return output.getvalue(), removed
