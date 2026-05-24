"""Detect and report invalid or malformed URLs in CSV fields."""

from urllib.parse import urlparse
from typing import List, Tuple, Dict
import re

ALLOWED_SCHEMES = {"http", "https", "ftp", "ftps"}


def is_valid_url(value: str) -> bool:
    """Return True if value is a well-formed URL with a recognised scheme."""
    try:
        result = urlparse(value.strip())
        if result.scheme not in ALLOWED_SCHEMES:
            return False
        if not result.netloc:
            return False
        # netloc must contain at least one dot (e.g. example.com)
        if "." not in result.netloc:
            return False
        return True
    except ValueError:
        return False


def looks_like_url(value: str) -> bool:
    """Heuristic: does the value look like it was intended to be a URL?"""
    stripped = value.strip().lower()
    return bool(
        re.match(r"https?://", stripped)
        or re.match(r"ftp[s]?://", stripped)
        or re.match(r"www\.", stripped)
    )


def find_invalid_urls(
    rows: List[List[str]], col_index: int
) -> List[Tuple[int, int, str]]:
    """Return (row_index, col_index, value) for cells that look like URLs but are invalid."""
    issues = []
    for row_idx, row in enumerate(rows):
        if col_index >= len(row):
            continue
        value = row[col_index]
        if looks_like_url(value) and not is_valid_url(value):
            issues.append((row_idx, col_index, value))
    return issues


def find_url_columns(
    rows: List[List[str]], threshold: float = 0.5
) -> List[int]:
    """Return column indices where at least *threshold* fraction of non-empty cells look like URLs."""
    if not rows:
        return []
    num_cols = max(len(r) for r in rows)
    url_cols = []
    for col_idx in range(num_cols):
        values = [r[col_idx] for r in rows if col_idx < len(r) and r[col_idx].strip()]
        if not values:
            continue
        url_count = sum(1 for v in values if looks_like_url(v))
        if url_count / len(values) >= threshold:
            url_cols.append(col_idx)
    return url_cols


def find_urlcheck_issues(
    rows: List[List[str]],
) -> Dict[str, object]:
    """Scan all likely URL columns and return a report of invalid URLs."""
    url_cols = find_url_columns(rows)
    all_issues = []
    for col_idx in url_cols:
        all_issues.extend(find_invalid_urls(rows, col_idx))
    return {
        "url_columns": url_cols,
        "invalid_urls": all_issues,
        "count": len(all_issues),
    }
