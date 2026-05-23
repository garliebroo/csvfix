import csv
import io
from dataclasses import dataclass, field
from typing import Optional

from csvfix.encoding import fix_encoding, write_fixed_file
from csvfix.delimiter import normalize_delimiter
from csvfix.whitespace import fix_whitespace_in_content
from csvfix.quotes import fix_quoting_in_content
from csvfix.lineendings import normalize_line_endings, LineEnding
from csvfix.bom import strip_bom
from csvfix.nulls import fix_nulls_in_content
from csvfix.duplicates import fix_duplicates_in_content
from csvfix.headers import fix_headers_in_content


@dataclass
class RepairOptions:
    fix_encoding: bool = True
    fix_bom: bool = True
    fix_line_endings: bool = True
    target_line_ending: LineEnding = LineEnding.LF
    fix_delimiter: bool = False
    target_delimiter: str = ","
    fix_whitespace: bool = True
    fix_quotes: bool = True
    fix_nulls: bool = True
    fix_duplicates: bool = False
    fix_headers: bool = True
    null_replacement: str = ""


@dataclass
class RepairReport:
    encoding_fixes: int = 0
    bom_removed: bool = False
    line_ending_fixes: int = 0
    delimiter_fixes: int = 0
    whitespace_fixes: int = 0
    quote_fixes: int = 0
    null_fixes: int = 0
    duplicate_fixes: int = 0
    header_fixes: int = 0
    issues: list = field(default_factory=list)


def total_fixes(report: RepairReport) -> int:
    return (
        report.encoding_fixes
        + report.line_ending_fixes
        + report.delimiter_fixes
        + report.whitespace_fixes
        + report.quote_fixes
        + report.null_fixes
        + report.duplicate_fixes
        + report.header_fixes
        + (1 if report.bom_removed else 0)
    )


def repair_file(
    input_path: str,
    output_path: str,
    options: Optional[RepairOptions] = None,
) -> RepairReport:
    if options is None:
        options = RepairOptions()

    report = RepairReport()

    raw_bytes = open(input_path, "rb").read()

    if options.fix_bom and raw_bytes[:3] == b"\xef\xbb\xbf":
        raw_bytes = raw_bytes[3:]
        report.bom_removed = True

    if options.fix_encoding:
        content, report.encoding_fixes = fix_encoding(raw_bytes)
    else:
        content = raw_bytes.decode("utf-8", errors="replace")

    if options.fix_line_endings:
        content, report.line_ending_fixes = normalize_line_endings(
            content, options.target_line_ending
        )

    if options.fix_delimiter:
        content = normalize_delimiter(content, options.target_delimiter)
        report.delimiter_fixes = 1

    if options.fix_whitespace:
        content, report.whitespace_fixes = fix_whitespace_in_content(content)

    if options.fix_quotes:
        content, report.quote_fixes = fix_quoting_in_content(content)

    if options.fix_nulls:
        content, report.null_fixes = fix_nulls_in_content(
            content, options.null_replacement
        )

    if options.fix_duplicates:
        content, report.duplicate_fixes = fix_duplicates_in_content(content)

    if options.fix_headers:
        content, report.header_fixes = fix_headers_in_content(content)

    write_fixed_file(output_path, content)
    return report
