# Email Check Integration

## Overview

The `emailcheck` module scans CSV files for columns that contain email addresses and validates each value against a standard email pattern.

## How It Works

1. **Column detection** — `find_email_columns` identifies likely email columns either by matching the word `email` in the header name or by checking that at least 50% of non-empty values in a column contain `@`.

2. **Validation** — `is_valid_email` applies a practical regex that requires a local part, `@`, a domain with at least one dot, and a TLD of two or more letters.

3. **Reporting** — `find_emailcheck_issues` returns a dict with:
   - `email_columns`: list of column indices identified as email columns
   - `invalid_emails`: list of `(row_index, col_index_str, value)` tuples
   - `count`: total number of invalid emails found

## Usage via Pipeline

Email checking is available as a report-only step in the repair pipeline (no auto-fix — invalid emails require human review).

```python
from csvfix.emailcheck import find_emailcheck_issues

with open('data.csv') as f:
    content = f.read()

report = find_emailcheck_issues(content)
print(f"Found {report['count']} invalid email(s)")
for row, col, val in report['invalid_emails']:
    print(f"  Row {row}, col {col}: {val!r}")
```

## Limitations

- The regex is intentionally simple; it will not catch all RFC 5321 edge cases.
- Columns are auto-detected on a best-effort basis; pass explicit column indices via `find_invalid_emails` for precise control.
- Internationalized email addresses (IDN) are not supported.
