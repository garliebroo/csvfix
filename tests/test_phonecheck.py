import pytest
from csvfix.phonecheck import (
    is_valid_phone,
    looks_like_phone,
    normalize_phone,
    find_phone_columns,
    find_invalid_phones,
    find_phonecheck_issues,
)


# --- is_valid_phone ---

def test_is_valid_phone_us_standard():
    assert is_valid_phone('(555) 123-4567') is True

def test_is_valid_phone_dashes():
    assert is_valid_phone('555-123-4567') is True

def test_is_valid_phone_digits_only():
    assert is_valid_phone('5551234567') is True

def test_is_valid_phone_with_country_code():
    assert is_valid_phone('+1-800-555-0199') is True

def test_is_valid_phone_international():
    assert is_valid_phone('+44 20 7946 0958') is True

def test_is_valid_phone_too_short():
    assert is_valid_phone('123') is False

def test_is_valid_phone_too_long():
    assert is_valid_phone('1234567890123456') is False

def test_is_valid_phone_empty():
    assert is_valid_phone('') is False

def test_is_valid_phone_letters():
    assert is_valid_phone('call-me-now') is False


# --- looks_like_phone ---

def test_looks_like_phone_phone():
    assert looks_like_phone('phone') is True

def test_looks_like_phone_mobile():
    assert looks_like_phone('Mobile') is True

def test_looks_like_phone_tel():
    assert looks_like_phone('tel') is True

def test_looks_like_phone_no_match():
    assert looks_like_phone('email') is False

def test_looks_like_phone_name():
    assert looks_like_phone('name') is False


# --- normalize_phone ---

def test_normalize_phone_digits_mode():
    assert normalize_phone('(555) 123-4567', fmt='digits') == '5551234567'

def test_normalize_phone_dashes_mode_10_digits():
    assert normalize_phone('5551234567', fmt='dashes') == '555-123-4567'

def test_normalize_phone_dashes_mode_non_10_digits_returns_original():
    assert normalize_phone('+1 800 555 0199', fmt='dashes') == '+1 800 555 0199'

def test_normalize_phone_empty():
    assert normalize_phone('') == ''


# --- find_phone_columns ---

def test_find_phone_columns_detects_phone():
    headers = ['name', 'phone', 'email']
    assert find_phone_columns(headers) == [1]

def test_find_phone_columns_multiple():
    headers = ['mobile', 'fax', 'address']
    assert find_phone_columns(headers) == [0, 1]

def test_find_phone_columns_none():
    assert find_phone_columns(['name', 'email', 'city']) == []


# --- find_invalid_phones / find_phonecheck_issues ---

def test_find_invalid_phones_all_valid():
    headers = ['name', 'phone']
    rows = [['Alice', '555-123-4567'], ['Bob', '(800) 999-0000']]
    assert find_invalid_phones(rows, headers) == []

def test_find_invalid_phones_detects_bad():
    headers = ['name', 'phone']
    rows = [['Alice', 'not-a-phone']]
    issues = find_invalid_phones(rows, headers)
    assert len(issues) == 1
    assert issues[0]['value'] == 'not-a-phone'

def test_find_invalid_phones_skips_empty_values():
    headers = ['phone']
    rows = [['']]
    assert find_invalid_phones(rows, headers) == []

def test_find_phonecheck_issues_returns_strings():
    headers = ['contact']
    rows = [['bad-number']]
    issues = find_phonecheck_issues(rows, headers)
    assert len(issues) == 1
    assert 'bad-number' in issues[0]
