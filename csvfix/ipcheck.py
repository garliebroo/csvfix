"""Detect and validate IP address fields in CSV data."""

import re
import csv
import io
from typing import List, Tuple, Optional

# Simple IPv4 pattern
_IPV4_RE = re.compile(
    r'^(\d{1,3}\.){3}\d{1,3}$'
)

# Simple IPv6 pattern (full and compressed)
_IPV6_RE = re.compile(
    r'^([0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}$'
    r'|^(([0-9a-fA-F]{1,4}:)*)?::([0-9a-fA-F]{1,4}:)*[0-9a-fA-F]{1,4}$'
    r'|^::$'
)


def is_valid_ipv4(value: str) -> bool:
    """Return True if value is a valid IPv4 address."""
    if not _IPV4_RE.match(value.strip()):
        return False
    parts = value.strip().split('.')
    return all(0 <= int(p) <= 255 for p in parts)


def is_valid_ipv6(value: str) -> bool:
    """Return True if value is a valid IPv6 address."""
    return bool(_IPV6_RE.match(value.strip()))


def is_valid_ip(value: str) -> bool:
    """Return True if value is a valid IPv4 or IPv6 address."""
    v = value.strip()
    return is_valid_ipv4(v) or is_valid_ipv6(v)


def looks_like_ip_column(values: List[str], threshold: float = 0.7) -> bool:
    """Return True if enough non-empty values in the column look like IPs."""
    non_empty = [v for v in values if v.strip()]
    if not non_empty:
        return False
    valid_count = sum(1 for v in non_empty if is_valid_ip(v))
    return (valid_count / len(non_empty)) >= threshold


def find_ip_columns(rows: List[List[str]], header: Optional[List[str]] = None) -> List[int]:
    """Return column indices that appear to contain IP addresses."""
    if not rows:
        return []
    num_cols = max(len(r) for r in rows)
    ip_cols = []
    for col_idx in range(num_cols):
        col_values = [row[col_idx] for row in rows if col_idx < len(row)]
        name = (header[col_idx].lower() if header and col_idx < len(header) else "")
        name_hint = any(kw in name for kw in ("ip", "addr", "address", "host"))
        if name_hint or looks_like_ip_column(col_values):
            ip_cols.append(col_idx)
    return ip_cols


def find_invalid_ips(rows: List[List[str]], header: Optional[List[str]] = None) -> List[Tuple[int, int, str]]:
    """Return list of (row_index, col_index, value) for invalid IP fields."""
    ip_cols = find_ip_columns(rows, header)
    issues = []
    for row_idx, row in enumerate(rows):
        for col_idx in ip_cols:
            if col_idx >= len(row):
                continue
            val = row[col_idx].strip()
            if val and not is_valid_ip(val):
                issues.append((row_idx, col_idx, row[col_idx]))
    return issues


def find_ipcheck_issues(content: str) -> List[str]:
    """Parse CSV content and return human-readable IP validation issue messages."""
    reader = csv.reader(io.StringIO(content))
    rows = list(reader)
    if not rows:
        return []
    header = rows[0]
    data_rows = rows[1:]
    invalid = find_invalid_ips(data_rows, header)
    messages = []
    for row_idx, col_idx, val in invalid:
        col_name = header[col_idx] if col_idx < len(header) else str(col_idx)
        messages.append(
            f"Row {row_idx + 2}, column '{col_name}': invalid IP address '{val}'"
        )
    return messages
