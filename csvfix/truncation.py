"""Detect and report fields that may have been truncated due to length limits."""

import csv
import io
from typing import Optional

DEFAULT_MAX_FIELD_LENGTH = 255


def find_truncated_fields(
    rows: list[list[str]],
    max_length: int = DEFAULT_MAX_FIELD_LENGTH,
    has_header: bool = True,
) -> list[dict]:
    """Return a list of issues for fields that meet or exceed max_length."""
    issues = []
    start = 1 if has_header else 0
    header = rows[0] if has_header and rows else []

    for row_idx, row in enumerate(rows[start:], start=start):
        for col_idx, field in enumerate(row):
            if len(field) >= max_length:
                col_name = header[col_idx] if col_idx < len(header) else str(col_idx)
                issues.append({
                    "row": row_idx,
                    "col": col_idx,
                    "col_name": col_name,
                    "length": len(field),
                    "max_length": max_length,
                    "value_preview": field[:40] + "..." if len(field) > 40 else field,
                })
    return issues


def get_field_length_stats(
    rows: list[list[str]],
    has_header: bool = True,
) -> dict[str, dict]:
    """Return per-column max and average field lengths."""
    start = 1 if has_header else 0
    header = rows[0] if has_header and rows else []
    stats: dict[str, list[int]] = {}

    for row in rows[start:]:
        for col_idx, field in enumerate(row):
            col_name = header[col_idx] if col_idx < len(header) else str(col_idx)
            stats.setdefault(col_name, []).append(len(field))

    return {
        col: {
            "max": max(lengths),
            "avg": round(sum(lengths) / len(lengths), 2),
            "count": len(lengths),
        }
        for col, lengths in stats.items()
    }


def find_truncation_issues(
    content: str,
    max_length: int = DEFAULT_MAX_FIELD_LENGTH,
    delimiter: str = ",",
    has_header: bool = True,
) -> list[dict]:
    """Parse CSV content and return truncation issues."""
    reader = csv.reader(io.StringIO(content), delimiter=delimiter)
    rows = list(reader)
    return find_truncated_fields(rows, max_length=max_length, has_header=has_header)
