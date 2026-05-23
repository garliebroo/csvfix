"""Detect and repair quoting issues in CSV fields."""

import csv
import io
from typing import List, Tuple


def find_unmatched_quotes(field: str) -> bool:
    """Return True if a field has unmatched/unescaped quote characters."""
    stripped = field.strip()
    if not stripped:
        return False
    # Count unescaped double quotes
    count = stripped.count('"') - stripped.count('""') * 2
    if stripped.startswith('"') and stripped.endswith('"') and len(stripped) > 1:
        count -= 2
    return count % 2 != 0


def normalize_quoting(field: str) -> str:
    """Ensure a field is properly quoted if it contains special characters."""
    needs_quoting = any(c in field for c in (',', ';', '\t', '\n', '"'))
    if not needs_quoting:
        return field
    # Escape existing double quotes by doubling them
    escaped = field.replace('"', '""')
    return f'"{escaped}"'


def fix_quotes_in_row(row: List[str]) -> List[str]:
    """Fix quoting issues in a single CSV row."""
    fixed = []
    for field in row:
        # Strip surrounding whitespace-padded quotes if malformed
        stripped = field.strip()
        if stripped.startswith('"') and not stripped.endswith('"'):
            stripped = stripped + '"'
        elif stripped.endswith('"') and not stripped.startswith('"'):
            stripped = '"' + stripped
        fixed.append(stripped)
    return fixed


def find_quoting_issues(content: str, delimiter: str = ',') -> List[Tuple[int, int, str]]:
    """Scan CSV content and return list of (row, col, description) for quoting issues."""
    issues = []
    reader = csv.reader(io.StringIO(content), delimiter=delimiter)
    for row_idx, row in enumerate(reader):
        for col_idx, field in enumerate(row):
            if find_unmatched_quotes(field):
                issues.append((row_idx, col_idx, f"Unmatched quote in field: {field!r}"))
    return issues


def fix_quoting_in_content(content: str, delimiter: str = ',') -> str:
    """Read CSV content, fix quoting issues, and return repaired content."""
    output = io.StringIO()
    reader = csv.reader(io.StringIO(content), delimiter=delimiter)
    writer = csv.writer(output, delimiter=delimiter, quoting=csv.QUOTE_MINIMAL)
    for row in reader:
        fixed_row = fix_quotes_in_row(row)
        writer.writerow(fixed_row)
    return output.getvalue()
