"""Detect and fix delimiter issues in CSV files."""

import csv
import io
from collections import Counter

COMMON_DELIMITERS = [",", ";", "\t", "|", ":"]


def detect_delimiter(content: str) -> str:
    """Sniff the delimiter from a sample of CSV content.

    Falls back to comma if detection fails.
    """
    sample = content[:4096]
    try:
        dialect = csv.Sniffer().sniff(sample, delimiters=",;\t|:")
        return dialect.delimiter
    except csv.Error:
        pass

    # Manual fallback: count occurrences per line and pick most consistent
    lines = [l for l in sample.splitlines() if l.strip()][:10]
    if not lines:
        return ","

    scores = {}
    for delim in COMMON_DELIMITERS:
        counts = [line.count(delim) for line in lines]
        if max(counts, default=0) > 0:
            # Prefer delimiters with consistent counts across lines
            variance = max(counts) - min(counts)
            scores[delim] = (sum(counts), -variance)

    if not scores:
        return ","

    return max(scores, key=lambda d: scores[d])


def normalize_delimiter(content: str, target: str = ",") -> str:
    """Re-serialize CSV content using the target delimiter."""
    source_delim = detect_delimiter(content)
    if source_delim == target:
        return content

    reader = csv.reader(io.StringIO(content), delimiter=source_delim)
    output = io.StringIO()
    writer = csv.writer(output, delimiter=target, lineterminator="\n")
    for row in reader:
        writer.writerow(row)
    return output.getvalue()


def has_inconsistent_columns(content: str, delimiter: str | None = None) -> bool:
    """Return True if rows have different column counts."""
    delim = delimiter or detect_delimiter(content)
    reader = csv.reader(io.StringIO(content), delimiter=delim)
    counts = [len(row) for row in reader if row]
    if len(counts) < 2:
        return False
    return len(set(counts)) > 1


def get_column_count_report(content: str, delimiter: str | None = None) -> dict:
    """Return a frequency map of column counts across rows."""
    delim = delimiter or detect_delimiter(content)
    reader = csv.reader(io.StringIO(content), delimiter=delim)
    counts = [len(row) for row in reader if row]
    return dict(Counter(counts))
