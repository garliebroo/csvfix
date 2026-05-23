# Row Length Checking

The `csvfix.rowlength` module detects and repairs rows whose field counts deviate from the expected column count.

## Functions

### `get_expected_column_count(rows)`
Returns the most common row length across all rows. Used as the baseline for comparison.

### `find_short_rows(rows, expected=None)`
Returns `(row_index, actual_length)` tuples for rows that have fewer fields than expected.

### `find_long_rows(rows, expected=None)`
Returns `(row_index, actual_length)` tuples for rows that have more fields than expected.

### `pad_short_rows(rows, expected=None, fill="")`
Pads short rows with a fill value (default empty string) so every row reaches the expected length.

### `truncate_long_rows(rows, expected=None)`
Truncates rows that exceed the expected length, dropping trailing fields.

### `find_rowlength_issues(rows)`
Returns a summary dictionary:
```python
{
    "expected_columns": int,
    "short_rows": [(row_index, actual_length), ...],
    "long_rows":  [(row_index, actual_length), ...],
    "total_issues": int,
}
```

## Usage

```python
import csv, io
from csvfix.rowlength import pad_short_rows, truncate_long_rows, find_rowlength_issues

with open("data.csv", newline="") as f:
    rows = list(csv.reader(f))

report = find_rowlength_issues(rows)
print(f"Found {report['total_issues']} row-length issues")

fixed = pad_short_rows(truncate_long_rows(rows))
```

## Integration with pipeline

`find_rowlength_issues` is called by `repair_file` in `csvfix/pipeline.py` when the `check_rowlength` option is enabled in `RepairOptions`.
