"""Main repair pipeline that applies all fixes to a CSV file."""

from dataclasses import dataclass, field
from typing import List, Optional

from csvfix.encoding import read_with_encoding, write_fixed_file, fix_encoding
from csvfix.bom import strip_bom_from_string, find_bom_issues
from csvfix.lineendings import normalize_line_endings, find_line_ending_issues
from csvfix.delimiter import normalize_delimiter, has_inconsistent_columns
from csvfix.whitespace import fix_whitespace_in_content, find_whitespace_issues
from csvfix.quotes import fix_quoting_in_content, find_quoting_issues
from csvfix.nulls import fix_nulls_in_content, find_null_issues


@dataclass
class RepairOptions:
    fix_encoding: bool = True
    fix_bom: bool = True
    fix_line_endings: bool = True
    target_line_ending: str = "lf"
    fix_delimiter: bool = False
    target_delimiter: str = ","
    fix_whitespace: bool = True
    fix_quotes: bool = True
    fix_nulls: bool = False
    null_replacement: str = ""
    custom_nulls: Optional[List[str]] = None
    encoding: Optional[str] = None


@dataclass
class RepairReport:
    original_encoding: str = "utf-8"
    bom_removed: bool = False
    line_endings_fixed: int = 0
    delimiter_changes: int = 0
    whitespace_fixes: int = 0
    quote_fixes: int = 0
    null_fixes: int = 0
    issues_found: List[str] = field(default_factory=list)

    @property
    def total_fixes(self) -> int:
        return (
            self.line_endings_fixed
            + self.delimiter_changes
            + self.whitespace_fixes
            + self.quote_fixes
            + self.null_fixes
            + (1 if self.bom_removed else 0)
        )


def repair_file(input_path: str, output_path: str, options: Optional[RepairOptions] = None) -> RepairReport:
    """Run all enabled repair steps on the given CSV file and write the result."""
    if options is None:
        options = RepairOptions()

    report = RepairReport()

    raw_bytes = open(input_path, "rb").read()
    content, encoding = read_with_encoding(input_path, options.encoding)
    report.original_encoding = encoding

    if options.fix_bom:
        bom_issues = find_bom_issues(raw_bytes)
        if bom_issues:
            report.bom_removed = True
            report.issues_found.extend(bom_issues)
            content = strip_bom_from_string(content)

    if options.fix_line_endings:
        le_issues = find_line_ending_issues(content)
        report.issues_found.extend(le_issues)
        content, report.line_endings_fixed = normalize_line_endings(content, options.target_line_ending)

    if options.fix_whitespace:
        ws_issues = find_whitespace_issues(content)
        report.issues_found.extend(ws_issues)
        content, report.whitespace_fixes = fix_whitespace_in_content(content)

    if options.fix_quotes:
        q_issues = find_quoting_issues(content)
        report.issues_found.extend(q_issues)
        content, report.quote_fixes = fix_quoting_in_content(content)

    if options.fix_nulls:
        null_issues = find_null_issues(content, options.custom_nulls)
        report.issues_found.extend([str(i) for i in null_issues])
        content, report.null_fixes = fix_nulls_in_content(
            content, options.null_replacement, options.custom_nulls
        )

    write_fixed_file(output_path, content, encoding)
    return report
