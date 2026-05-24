"""csvfix — detect and repair common encoding and formatting issues in CSV files."""

from csvfix.encoding import detect_encoding, fix_encoding
from csvfix.delimiter import detect_delimiter, normalize_delimiter
from csvfix.whitespace import fix_whitespace_in_content, find_whitespace_issues
from csvfix.quotes import fix_quoting_in_content, find_quoting_issues
from csvfix.lineendings import normalize_line_endings, find_line_ending_issues
from csvfix.bom import strip_bom, find_bom_issues
from csvfix.nulls import fix_nulls_in_content, find_null_issues
from csvfix.duplicates import fix_duplicates_in_content, find_duplicate_issues
from csvfix.typecheck import find_typecheck_issues
from csvfix.truncation import find_truncation_issues
from csvfix.headers import fix_headers_in_content, find_header_issues
from csvfix.emptycols import fix_empty_columns_in_content, find_empty_column_issues
from csvfix.rowlength import find_rowlength_issues
from csvfix.specialchars import find_specialchar_issues
from csvfix.outliers import find_outlier_issues
from csvfix.fieldlength import find_fieldlength_issues
from csvfix.dateformat import fix_dates_in_content, find_date_format_issues
from csvfix.emailcheck import find_emailcheck_issues
from csvfix.pipeline import RepairOptions, RepairReport, repair_file

__all__ = [
    # encoding
    'detect_encoding',
    'fix_encoding',
    # delimiter
    'detect_delimiter',
    'normalize_delimiter',
    # whitespace
    'fix_whitespace_in_content',
    'find_whitespace_issues',
    # quotes
    'fix_quoting_in_content',
    'find_quoting_issues',
    # line endings
    'normalize_line_endings',
    'find_line_ending_issues',
    # BOM
    'strip_bom',
    'find_bom_issues',
    # nulls
    'fix_nulls_in_content',
    'find_null_issues',
    # duplicates
    'fix_duplicates_in_content',
    'find_duplicate_issues',
    # type check
    'find_typecheck_issues',
    # truncation
    'find_truncation_issues',
    # headers
    'fix_headers_in_content',
    'find_header_issues',
    # empty columns
    'fix_empty_columns_in_content',
    'find_empty_column_issues',
    # row length
    'find_rowlength_issues',
    # special chars
    'find_specialchar_issues',
    # outliers
    'find_outlier_issues',
    # field length
    'find_fieldlength_issues',
    # date format
    'fix_dates_in_content',
    'find_date_format_issues',
    # email check
    'find_emailcheck_issues',
    # pipeline
    'RepairOptions',
    'RepairReport',
    'repair_file',
]
