"""Detect and report rows with unexpected lengths (too few or too many fields)."""

from collections import Counter
from typing import List, Tuple, Dict


def get_expected_column_count(rows: List[List[str]]) -> int:
    """Return the most common row length, treating it as the expected column count."""
    if not rows:
        return 0
    counts = Counter(len(row) for row in rows)
    return counts.most_common(1)[0][0]


def find_short_rows(
    rows: List[List[str]], expected: int = None
) -> List[Tuple[int, int]]:
    """Return (row_index, actual_length) for rows shorter than expected."""
    if expected is None:
        expected = get_expected_column_count(rows)
    return [
        (i, len(row))
        for i, row in enumerate(rows)
        if len(row) < expected
    ]


def find_long_rows(
    rows: List[List[str]], expected: int = None
) -> List[Tuple[int, int]]:
    """Return (row_index, actual_length) for rows longer than expected."""
    if expected is None:
        expected = get_expected_column_count(rows)
    return [
        (i, len(row))
        for i, row in enumerate(rows)
        if len(row) > expected
    ]


def pad_short_rows(
    rows: List[List[str]], expected: int = None, fill: str = ""
) -> List[List[str]]:
    """Pad short rows with `fill` so all rows reach `expected` length."""
    if expected is None:
        expected = get_expected_column_count(rows)
    result = []
    for row in rows:
        if len(row) < expected:
            row = row + [fill] * (expected - len(row))
        result.append(row)
    return result


def truncate_long_rows(
    rows: List[List[str]], expected: int = None
) -> List[List[str]]:
    """Truncate rows that exceed `expected` length."""
    if expected is None:
        expected = get_expected_column_count(rows)
    return [row[:expected] for row in rows]


def find_rowlength_issues(rows: List[List[str]]) -> Dict:
    """Return a summary dict of row length issues found."""
    expected = get_expected_column_count(rows)
    short = find_short_rows(rows, expected)
    long_ = find_long_rows(rows, expected)
    return {
        "expected_columns": expected,
        "short_rows": short,
        "long_rows": long_,
        "total_issues": len(short) + len(long_),
    }
