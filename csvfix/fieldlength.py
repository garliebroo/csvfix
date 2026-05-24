"""Detect and fix fields that exceed a maximum allowed byte or character length."""

import csv
import io
from typing import List, Tuple, Dict, Optional


DEFAULT_MAX_FIELD_LENGTH = 131072  # 128 KB, same as Python's csv default


def find_long_fields(
    rows: List[List[str]],
    max_length: int = DEFAULT_MAX_FIELD_LENGTH,
    use_bytes: bool = False,
) -> List[Tuple[int, int, int]]:
    """Return list of (row_index, col_index, length) for fields exceeding max_length."""
    issues = []
    for row_idx, row in enumerate(rows):
        for col_idx, field in enumerate(row):
            length = len(field.encode("utf-8")) if use_bytes else len(field)
            if length > max_length:
                issues.append((row_idx, col_idx, length))
    return issues


def truncate_long_fields(
    rows: List[List[str]],
    max_length: int = DEFAULT_MAX_FIELD_LENGTH,
    use_bytes: bool = False,
    suffix: str = "",
) -> Tuple[List[List[str]], int]:
    """Truncate fields that exceed max_length. Returns (new_rows, fix_count)."""
    fix_count = 0
    result = []
    for row in rows:
        new_row = []
        for field in row:
            if use_bytes:
                encoded = field.encode("utf-8")
                if len(encoded) > max_length:
                    truncated = encoded[: max_length - len(suffix.encode("utf-8"))].decode(
                        "utf-8", errors="ignore"
                    )
                    new_row.append(truncated + suffix)
                    fix_count += 1
                else:
                    new_row.append(field)
            else:
                if len(field) > max_length:
                    new_row.append(field[: max_length - len(suffix)] + suffix)
                    fix_count += 1
                else:
                    new_row.append(field)
        result.append(new_row)
    return result, fix_count


def get_field_length_report(rows: List[List[str]]) -> Dict[int, Dict[str, int]]:
    """Return per-column stats: min, max, avg field length."""
    if not rows:
        return {}
    num_cols = max(len(r) for r in rows)
    report: Dict[int, Dict[str, int]] = {}
    for col_idx in range(num_cols):
        lengths = [len(row[col_idx]) for row in rows if col_idx < len(row)]
        if lengths:
            report[col_idx] = {
                "min": min(lengths),
                "max": max(lengths),
                "avg": sum(lengths) // len(lengths),
            }
    return report


def find_fieldlength_issues(
    content: str,
    max_length: int = DEFAULT_MAX_FIELD_LENGTH,
    use_bytes: bool = False,
) -> List[str]:
    """Parse CSV content and return human-readable issue descriptions."""
    reader = csv.reader(io.StringIO(content))
    rows = list(reader)
    issues_found = find_long_fields(rows, max_length=max_length, use_bytes=use_bytes)
    unit = "bytes" if use_bytes else "chars"
    return [
        f"Row {r}, col {c}: field length {length} exceeds max {max_length} {unit}"
        for r, c, length in issues_found
    ]
