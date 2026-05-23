"""High-level repair pipeline combining encoding, delimiter, and whitespace fixes."""

from dataclasses import dataclass, field
from pathlib import Path

from csvfix.encoding import detect_encoding, read_with_encoding, write_fixed_file
from csvfix.delimiter import detect_delimiter, normalize_delimiter, has_inconsistent_columns
from csvfix.whitespace import fix_whitespace_in_content, find_whitespace_issues


@dataclass
class RepairOptions:
    target_delimiter: str = ","
    strip_whitespace: bool = True
    collapse_whitespace: bool = False
    target_encoding: str = "utf-8"


@dataclass
class RepairReport:
    source_encoding: str = "unknown"
    source_delimiter: str = ","
    encoding_changed: bool = False
    delimiter_changed: bool = False
    whitespace_issues_found: int = 0
    inconsistent_columns: bool = False
    warnings: list[str] = field(default_factory=list)


def repair_file(
    input_path: str | Path,
    output_path: str | Path,
    options: RepairOptions | None = None,
) -> RepairReport:
    """Run the full repair pipeline on a CSV file.

    Reads the file, applies all enabled fixes, writes the result, and
    returns a summary report.
    """
    opts = options or RepairOptions()
    report = RepairReport()

    # --- encoding ---
    encoding = detect_encoding(str(input_path))
    report.source_encoding = encoding
    content = read_with_encoding(str(input_path), encoding)
    report.encoding_changed = encoding.lower().replace("-", "") != opts.target_encoding.lower().replace("-", "")

    # --- delimiter ---
    delim = detect_delimiter(content)
    report.source_delimiter = delim
    report.delimiter_changed = delim != opts.target_delimiter
    content = normalize_delimiter(content, target=opts.target_delimiter)

    # --- column consistency check ---
    report.inconsistent_columns = has_inconsistent_columns(
        content, delimiter=opts.target_delimiter
    )
    if report.inconsistent_columns:
        report.warnings.append("Inconsistent column counts detected after delimiter fix.")

    # --- whitespace ---
    ws_issues = find_whitespace_issues(content, delimiter=opts.target_delimiter)
    report.whitespace_issues_found = len(ws_issues)
    content = fix_whitespace_in_content(
        content,
        delimiter=opts.target_delimiter,
        strip=opts.strip_whitespace,
        collapse=opts.collapse_whitespace,
    )

    # --- write output ---
    write_fixed_file(str(output_path), content, encoding=opts.target_encoding)

    return report
