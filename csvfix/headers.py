import csv
import io
from typing import List, Optional, Tuple


def detect_header_row(rows: List[List[str]]) -> bool:
    """Heuristic: first row is a header if it contains no numeric-looking values."""
    if not rows:
        return False
    first_row = rows[0]
    if not first_row:
        return False
    numeric_count = 0
    for field in first_row:
        stripped = field.strip()
        try:
            float(stripped)
            numeric_count += 1
        except ValueError:
            pass
    return numeric_count == 0


def find_duplicate_headers(headers: List[str]) -> List[Tuple[str, List[int]]]:
    """Return list of (header_name, [indices]) for any duplicated header names."""
    seen = {}
    for i, h in enumerate(headers):
        key = h.strip().lower()
        seen.setdefault(key, []).append(i)
    return [(k, idxs) for k, idxs in seen.items() if len(idxs) > 1]


def normalize_header_names(headers: List[str]) -> List[str]:
    """Strip whitespace and lowercase header names."""
    return [h.strip().lower().replace(" ", "_") for h in headers]


def find_header_issues(content: str) -> List[str]:
    """Return a list of human-readable issue descriptions for header problems."""
    issues = []
    reader = csv.reader(io.StringIO(content))
    rows = list(reader)
    if not rows:
        return issues

    if not detect_header_row(rows):
        issues.append("First row may not be a header (contains numeric values)")
        return issues

    headers = rows[0]
    dupes = find_duplicate_headers(headers)
    for name, idxs in dupes:
        issues.append(f"Duplicate header '{name}' at columns {idxs}")

    for i, h in enumerate(headers):
        if h != h.strip():
            issues.append(f"Header at column {i} has surrounding whitespace: {repr(h)}")

    return issues


def fix_headers_in_content(content: str) -> Tuple[str, int]:
    """Normalize headers in CSV content. Returns (fixed_content, fix_count)."""
    reader = csv.reader(io.StringIO(content))
    rows = list(reader)
    if not rows:
        return content, 0

    fix_count = 0
    if detect_header_row(rows):
        original = rows[0]
        fixed = normalize_header_names(original)
        fix_count = sum(1 for a, b in zip(original, fixed) if a != b)
        rows[0] = fixed

    out = io.StringIO()
    writer = csv.writer(out)
    writer.writerows(rows)
    return out.getvalue(), fix_count
