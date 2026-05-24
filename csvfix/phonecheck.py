import re
from typing import Optional

# Common phone number patterns
_PHONE_PATTERNS = [
    re.compile(r'^\+?1?[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}$'),  # US/CA
    re.compile(r'^\+?\d{1,3}[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}$'),  # International
]

_PHONE_COLUMN_HINTS = {'phone', 'telephone', 'tel', 'mobile', 'cell', 'fax', 'contact'}


def is_valid_phone(value: str) -> bool:
    """Return True if value looks like a valid phone number."""
    cleaned = value.strip()
    if not cleaned:
        return False
    digits = re.sub(r'\D', '', cleaned)
    if len(digits) < 7 or len(digits) > 15:
        return False
    return any(p.match(cleaned) for p in _PHONE_PATTERNS)


def looks_like_phone(header: str) -> bool:
    """Return True if the column header suggests a phone number field."""
    return header.strip().lower() in _PHONE_COLUMN_HINTS


def normalize_phone(value: str, fmt: str = 'digits') -> Optional[str]:
    """Normalize a phone number to a consistent format.

    fmt options:
      'digits'  -> strip all non-digit characters
      'dashes'  -> NXX-NXX-XXXX for 10-digit US numbers
    """
    cleaned = value.strip()
    if not cleaned:
        return cleaned
    digits = re.sub(r'\D', '', cleaned)
    if fmt == 'digits':
        return digits
    if fmt == 'dashes' and len(digits) == 10:
        return f'{digits[:3]}-{digits[3:6]}-{digits[6:]}'
    return cleaned


def find_phone_columns(headers: list[str]) -> list[int]:
    """Return indices of columns that appear to contain phone numbers."""
    return [i for i, h in enumerate(headers) if looks_like_phone(h)]


def find_invalid_phones(rows: list[list[str]], headers: list[str]) -> list[dict]:
    """Return a list of issues for invalid phone numbers in phone-like columns."""
    issues = []
    phone_cols = find_phone_columns(headers)
    for row_idx, row in enumerate(rows):
        for col_idx in phone_cols:
            if col_idx >= len(row):
                continue
            val = row[col_idx]
            if val.strip() and not is_valid_phone(val):
                issues.append({
                    'row': row_idx,
                    'col': col_idx,
                    'header': headers[col_idx],
                    'value': val,
                })
    return issues


def find_phonecheck_issues(rows: list[list[str]], headers: list[str]) -> list[str]:
    """Return human-readable issue strings for invalid phone numbers."""
    bad = find_invalid_phones(rows, headers)
    return [
        f"Row {i['row']}, col '{i['header']}': invalid phone '{i['value']}'"
        for i in bad
    ]
