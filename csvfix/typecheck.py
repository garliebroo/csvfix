"""Utilities for detecting and reporting type inconsistencies in CSV columns."""

import re
import csv
import io
from collections import Counter
from typing import List, Dict, Optional, Tuple

_INT_RE = re.compile(r"^-?\d+$")
_FLOAT_RE = re.compile(r"^-?\d+\.\d*$|^-?\.\d+$")
_BOOL_VALUES = {"true", "false", "yes", "no", "1", "0"}


def infer_type(value: str) -> str:
    """Infer the type of a single string value."""
    v = value.strip()
    if v == "":
        return "empty"
    if _INT_RE.match(v):
        return "int"
    if _FLOAT_RE.match(v):
        return "float"
    if v.lower() in _BOOL_VALUES:
        return "bool"
    return "string"


def get_column_types(rows: List[List[str]]) -> Dict[int, Counter]:
    """Return a Counter of inferred types per column index."""
    col_types: Dict[int, Counter] = {}
    for row in rows:
        for i, field in enumerate(row):
            if i not in col_types:
                col_types[i] = Counter()
            col_types[i][infer_type(field)] += 1
    return col_types


def find_type_inconsistencies(
    col_types: Dict[int, Counter],
    header: Optional[List[str]] = None,
) -> List[str]:
    """Return human-readable messages for columns with mixed non-empty types."""
    issues = []
    for col_idx, counts in col_types.items():
        non_empty = {t: c for t, c in counts.items() if t != "empty"}
        if len(non_empty) > 1:
            col_name = (
                header[col_idx]
                if header and col_idx < len(header)
                else str(col_idx)
            )
            type_summary = ", ".join(
                f"{t}({c})" for t, c in sorted(non_empty.items())
            )
            issues.append(
                f"Column '{col_name}' has mixed types: {type_summary}"
            )
    return issues


def find_typecheck_issues(content: str, has_header: bool = True) -> List[str]:
    """Parse CSV content and return type inconsistency issues."""
    reader = csv.reader(io.StringIO(content))
    rows = list(reader)
    if not rows:
        return []

    header: Optional[List[str]] = None
    data_rows = rows
    if has_header and len(rows) > 1:
        header = rows[0]
        data_rows = rows[1:]

    col_types = get_column_types(data_rows)
    return find_type_inconsistencies(col_types, header)
