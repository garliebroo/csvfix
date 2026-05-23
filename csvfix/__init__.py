"""csvfix — detect and repair common encoding and formatting issues in CSV files."""

from csvfix.pipeline import RepairOptions, RepairReport, repair_file, total_fixes
from csvfix.encoding import detect_encoding, fix_encoding
from csvfix.delimiter import detect_delimiter, normalize_delimiter
from csvfix.whitespace import fix_whitespace_in_content, find_whitespace_issues
from csvfix.quotes import fix_quoting_in_content, find_quoting_issues
from csvfix.lineendings import detect_line_ending, normalize_line_endings, LineEnding
from csvfix.bom import detect_bom, strip_bom, find_bom_issues
from csvfix.nulls import fix_nulls_in_content, find_null_issues
from csvfix.duplicates import fix_duplicates_in_content, find_duplicate_issues
from csvfix.typecheck import find_typecheck_issues
from csvfix.truncation import find_truncation_issues
from csvfix.headers import (
    detect_header_row,
    find_duplicate_headers,
    normalize_header_names,
    find_header_issues,
    fix_headers_in_content,
)

__all__ = [
    "RepairOptions",
    "RepairReport",
    "repair_file",
    "total_fixes",
    "detect_encoding",
    "fix_encoding",
    "detect_delimiter",
    "normalize_delimiter",
    "fix_whitespace_in_content",
    "find_whitespace_issues",
    "fix_quoting_in_content",
    "find_quoting_issues",
    "detect_line_ending",
    "normalize_line_endings",
    "LineEnding",
    "detect_bom",
    "strip_bom",
    "find_bom_issues",
    "fix_nulls_in_content",
    "find_null_issues",
    "fix_duplicates_in_content",
    "find_duplicate_issues",
    "find_typecheck_issues",
    "find_truncation_issues",
    "detect_header_row",
    "find_duplicate_headers",
    "normalize_header_names",
    "find_header_issues",
    "fix_headers_in_content",
]
