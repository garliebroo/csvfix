"""Detect and normalize inconsistent date formats in CSV fields."""

import re
from typing import Optional

DATE_PATTERNS = [
    (re.compile(r'^\d{4}-\d{2}-\d{2}$'), 'ISO'),          # 2024-01-15
    (re.compile(r'^\d{2}/\d{2}/\d{4}$'), 'MDY'),          # 01/15/2024
    (re.compile(r'^\d{2}-\d{2}-\d{4}$'), 'MDY_DASH'),     # 01-15-2024
    (re.compile(r'^\d{2}\.\d{2}\.\d{4}$'), 'DMY_DOT'),   # 15.01.2024
    (re.compile(r'^\d{1,2}/\d{1,2}/\d{2}$'), 'SHORT'),   # 1/5/24
]


def detect_date_format(value: str) -> Optional[str]:
    """Return a format label if value looks like a date, else None."""
    value = value.strip()
    for pattern, label in DATE_PATTERNS:
        if pattern.match(value):
            return label
    return None


def normalize_date_field(value: str, target_format: str = 'ISO') -> str:
    """Attempt to normalize a date string to the target format.

    Only MDY (MM/DD/YYYY) -> ISO conversion is supported for now.
    Returns original value if conversion is not possible.
    """
    fmt = detect_date_format(value)
    if fmt == target_format:
        return value
    if fmt in ('MDY', 'MDY_DASH') and target_format == 'ISO':
        sep = '/' if fmt == 'MDY' else '-'
        parts = value.split(sep)
        if len(parts) == 3:
            mm, dd, yyyy = parts
            return f"{yyyy}-{mm.zfill(2)}-{dd.zfill(2)}"
    return value


def find_date_format_issues(rows: list[list[str]]) -> list[dict]:
    """Scan all fields and report columns with mixed date formats."""
    if not rows:
        return []

    col_formats: dict[int, set] = {}
    for row in rows:
        for col_idx, field in enumerate(row):
            fmt = detect_date_format(field)
            if fmt:
                col_formats.setdefault(col_idx, set()).add(fmt)

    issues = []
    for col_idx, formats in col_formats.items():
        if len(formats) > 1:
            issues.append({
                'column': col_idx,
                'formats_found': sorted(formats),
                'message': f"Column {col_idx} has mixed date formats: {sorted(formats)}",
            })
    return issues


def fix_dates_in_content(
    rows: list[list[str]], target_format: str = 'ISO'
) -> tuple[list[list[str]], int]:
    """Normalize all date fields in rows to target_format. Returns (rows, fix_count)."""
    fixed_rows = []
    fix_count = 0
    for row in rows:
        new_row = []
        for field in row:
            normalized = normalize_date_field(field, target_format)
            if normalized != field:
                fix_count += 1
            new_row.append(normalized)
        fixed_rows.append(new_row)
    return fixed_rows, fix_count
