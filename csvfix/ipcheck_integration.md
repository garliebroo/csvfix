# IP Address Check Integration

## Overview

The `ipcheck` module detects columns containing IP addresses and validates each
value as either a valid IPv4 or IPv6 address. It integrates with the csvfix
pipeline as a detection-only pass (no auto-repair, since "fixing" a bad IP
requires domain knowledge).

## Functions

### `is_valid_ipv4(value: str) -> bool`
Returns `True` if the value is a syntactically valid IPv4 address with all
octets in the range 0–255.

### `is_valid_ipv6(value: str) -> bool`
Returns `True` if the value matches a full or compressed IPv6 address.

### `is_valid_ip(value: str) -> bool`
Returns `True` for either valid IPv4 or IPv6.

### `looks_like_ip_column(values, threshold=0.7) -> bool`
Heuristic: returns `True` if at least `threshold` fraction of non-empty values
in the list are valid IPs.

### `find_ip_columns(rows, header=None) -> List[int]`
Returns column indices that appear to hold IP addresses, using both name hints
(`ip`, `addr`, `address`, `host`) and value heuristics.

### `find_invalid_ips(rows, header=None) -> List[Tuple[int, int, str]]`
Returns `(row_index, col_index, value)` tuples for every invalid IP found in
auto-detected IP columns.

### `find_ipcheck_issues(content: str) -> List[str]`
Top-level entry point. Parses CSV content, runs validation, and returns
human-readable issue strings suitable for the pipeline report.

## Example

```python
from csvfix.ipcheck import find_ipcheck_issues

content = """host,ip_address
web01,192.168.1.10
web02,999.0.0.1
web03,::1
"""

for issue in find_ipcheck_issues(content):
    print(issue)
# Row 3, column 'ip_address': invalid IP address '999.0.0.1'
```

## Pipeline Integration

Add `find_ipcheck_issues` to the issue-gathering step in `pipeline.py` alongside
other validators like `find_emailcheck_issues` and `find_urlcheck_issues`.
No repair step is registered since correcting an invalid IP is ambiguous.
