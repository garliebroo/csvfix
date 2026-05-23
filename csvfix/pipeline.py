"""High-level repair pipeline combining all csvfix modules."""

from dataclasses import dataclass, field
from typing import Optional

from csvfix.encoding import detect_encoding, read_with_encoding, write_fixed_file
from csvfix.delimiter import detect_delimiter, normalize_delimiter, has_inconsistent_columns
from csvfix.whitespace import fix_whitespace_in_content, find_whitespace_issues
from csvfix.quotes import fix_quoting_in_content, find_quoting_issues


@dataclass
class RepairOptions:
    fix_encoding: bool = True
    fix_delimiter: bool = True
    target_delimiter: str = ","
    fix_whitespace: bool = True
    fix_quotes: bool = True
    output_path: Optional[str] = None


@dataclass
class RepairReport:
    input_path: str
    encoding_detected: str = "unknown"
    delimiter_detected: str = ","
    whitespace_issues: int = 0
    quoting_issues: int = 0
    inconsistent_columns: bool = False
    steps_applied: list = field(default_factory=list)
    output_path: Optional[str] = None


def repair_file(input_path: str, options: Optional[RepairOptions] = None) -> RepairReport:
    """Run the full repair pipeline on a CSV file."""
    if options is None:
        options = RepairOptions()

    report = RepairReport(input_path=input_path)

    # Step 1: Encoding
    encoding = detect_encoding(input_path)
    report.encoding_detected = encoding
    content = read_with_encoding(input_path, encoding=encoding)

    if options.fix_encoding:
        report.steps_applied.append("encoding")

    # Step 2: Delimiter
    delimiter = detect_delimiter(content)
    report.delimiter_detected = delimiter
    report.inconsistent_columns = has_inconsistent_columns(content, delimiter)

    if options.fix_delimiter and delimiter != options.target_delimiter:
        content = normalize_delimiter(content, from_delimiter=delimiter,
                                      to_delimiter=options.target_delimiter)
        delimiter = options.target_delimiter
        report.steps_applied.append("delimiter")

    # Step 3: Whitespace
    ws_issues = find_whitespace_issues(content)
    report.whitespace_issues = len(ws_issues)

    if options.fix_whitespace and ws_issues:
        content = fix_whitespace_in_content(content)
        report.steps_applied.append("whitespace")

    # Step 4: Quotes
    q_issues = find_quoting_issues(content, delimiter=delimiter)
    report.quoting_issues = len(q_issues)

    if options.fix_quotes and q_issues:
        content = fix_quoting_in_content(content, delimiter=delimiter)
        report.steps_applied.append("quotes")

    # Write output
    out_path = options.output_path or input_path
    write_fixed_file(out_path, content)
    report.output_path = out_path

    return report
