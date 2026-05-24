# Date Format Detection & Normalization

## Overview

`csvfix/dateformat.py` detects inconsistent date formats across CSV columns and
normalizes them to a single target format (default: ISO `YYYY-MM-DD`).

## Supported Formats

| Label      | Example      | Pattern              |
|------------|--------------|----------------------|
| ISO        | 2024-01-15   | `YYYY-MM-DD`         |
| MDY        | 01/15/2024   | `MM/DD/YYYY`         |
| MDY_DASH   | 01-15-2024   | `MM-DD-YYYY`         |
| DMY_DOT    | 15.01.2024   | `DD.MM.YYYY`         |
| SHORT      | 1/5/24       | `M/D/YY`             |

## Functions

### `detect_date_format(value) -> Optional[str]`
Returns a format label string if `value` matches a known date pattern,
otherwise `None`. Strips surrounding whitespace before matching.

### `normalize_date_field(value, target_format='ISO') -> str`
Converts a date string to `target_format`. Currently supports MDY and
MDY_DASH → ISO. Returns the original string unchanged if conversion is
not supported.

### `find_date_format_issues(rows) -> list[dict]`
Scans all fields in `rows`. Returns one issue dict per column that
contains more than one distinct date format. Each dict includes:
- `column` — zero-based column index
- `formats_found` — sorted list of format labels seen
- `message` — human-readable description

### `fix_dates_in_content(rows, target_format='ISO') -> (rows, int)`
Applies `normalize_date_field` to every field in `rows`. Returns the
updated rows and the total number of fields that were changed.

## Pipeline Integration

Add to `RepairOptions` in `pipeline.py`:

```python
fix_dates: bool = True
date_target_format: str = 'ISO'
```

And in `repair_file`, after loading rows:

```python
if options.fix_dates:
    rows, n = fix_dates_in_content(rows, options.date_target_format)
    report.date_fixes = n
```
