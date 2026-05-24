"""Detect and report invalid or suspicious email addresses in CSV fields."""

import re
import csv
import io
from typing import List, Tuple, Dict

# Basic but practical email regex
_EMAIL_RE = re.compile(
    r'^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$'
)


def is_valid_email(value: str) -> bool:
    """Return True if value looks like a valid email address."""
    return bool(_EMAIL_RE.match(value.strip()))


def looks_like_email(value: str) -> bool:
    """Heuristic: does this field look like it was intended to be an email?"""
    v = value.strip()
    return '@' in v


def find_invalid_emails(
    rows: List[List[str]],
    col_index: int,
    has_header: bool = True,
) -> List[Tuple[int, str, str]]:
    """Scan a single column for invalid email values.

    Returns a list of (row_index, column_index_str, value) tuples
    for rows where the field looks like an email but fails validation.
    """
    issues = []
    start = 1 if has_header else 0
    for i, row in enumerate(rows[start:], start=start):
        if col_index >= len(row):
            continue
        value = row[col_index]
        if looks_like_email(value) and not is_valid_email(value):
            issues.append((i, str(col_index), value))
    return issues


def find_email_columns(rows: List[List[str]], has_header: bool = True) -> List[int]:
    """Return indices of columns that appear to contain email addresses."""
    if not rows:
        return []
    header = rows[0] if has_header else None
    sample_rows = rows[1:] if has_header else rows
    if not sample_rows:
        return []
    num_cols = max(len(r) for r in sample_rows)
    email_cols = []
    for col in range(num_cols):
        # Check header name hint
        if header and col < len(header) and 'email' in header[col].lower():
            email_cols.append(col)
            continue
        # Check if majority of non-empty values contain '@'
        values = [r[col] for r in sample_rows if col < len(r) and r[col].strip()]
        if values and sum(1 for v in values if '@' in v) / len(values) >= 0.5:
            email_cols.append(col)
    return email_cols


def find_emailcheck_issues(
    content: str,
    delimiter: str = ',',
    has_header: bool = True,
) -> Dict:
    """Parse CSV content and return a report of email validation issues."""
    reader = csv.reader(io.StringIO(content), delimiter=delimiter)
    rows = list(reader)
    email_cols = find_email_columns(rows, has_header=has_header)
    all_issues = []
    for col in email_cols:
        all_issues.extend(find_invalid_emails(rows, col, has_header=has_header))
    return {
        'email_columns': email_cols,
        'invalid_emails': all_issues,
        'count': len(all_issues),
    }
