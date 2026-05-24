# Phone Number Validation Integration

## Overview

`csvfix/phonecheck.py` detects and reports invalid phone numbers in CSV files by
automatically identifying phone-like columns based on their header names.

## Detected Column Names

Columns with any of these headers (case-insensitive) are checked:

- `phone`, `telephone`, `tel`
- `mobile`, `cell`
- `fax`, `contact`

## Validation Rules

A phone number is considered **valid** if:

1. It contains between 7 and 15 digits after stripping non-digit characters.
2. It matches a known US/Canadian or international format pattern.

Examples of valid values:
- `(555) 123-4567`
- `555-123-4567`
- `+1-800-555-0199`
- `+44 20 7946 0958`

Examples of invalid values:
- `123` (too short)
- `call-me-now` (non-numeric)
- `1234567890123456` (too long)

## Normalization

Use `normalize_phone(value, fmt=...)` to standardize values:

| `fmt`     | Result                              |
|-----------|-------------------------------------|
| `'digits'`| Strips all non-digit characters     |
| `'dashes'`| `NXX-NXX-XXXX` for 10-digit numbers |

Non-10-digit numbers in `'dashes'` mode are returned as-is.

## Pipeline Integration

```python
from csvfix.phonecheck import find_phonecheck_issues

issues = find_phonecheck_issues(rows, headers)
for issue in issues:
    print(issue)
```

This module is detection-only; it does not modify rows. Normalization must be
applied explicitly via `normalize_phone`.
