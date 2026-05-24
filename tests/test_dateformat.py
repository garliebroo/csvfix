"""Tests for csvfix.dateformat module."""

import pytest
from csvfix.dateformat import (
    detect_date_format,
    normalize_date_field,
    find_date_format_issues,
    fix_dates_in_content,
)


def test_detect_date_format_iso():
    assert detect_date_format('2024-01-15') == 'ISO'


def test_detect_date_format_mdy_slash():
    assert detect_date_format('01/15/2024') == 'MDY'


def test_detect_date_format_mdy_dash():
    assert detect_date_format('01-15-2024') == 'MDY_DASH'


def test_detect_date_format_dmy_dot():
    assert detect_date_format('15.01.2024') == 'DMY_DOT'


def test_detect_date_format_short():
    assert detect_date_format('1/5/24') == 'SHORT'


def test_detect_date_format_not_a_date():
    assert detect_date_format('hello') is None


def test_detect_date_format_empty():
    assert detect_date_format('') is None


def test_detect_date_format_strips_whitespace():
    assert detect_date_format('  2024-03-10  ') == 'ISO'


def test_normalize_date_field_already_iso():
    assert normalize_date_field('2024-01-15') == '2024-01-15'


def test_normalize_date_field_mdy_to_iso():
    assert normalize_date_field('01/15/2024') == '2024-01-15'


def test_normalize_date_field_mdy_dash_to_iso():
    assert normalize_date_field('01-15-2024') == '2024-01-15'


def test_normalize_date_field_unsupported_format_unchanged():
    assert normalize_date_field('15.01.2024') == '15.01.2024'


def test_normalize_date_field_non_date_unchanged():
    assert normalize_date_field('not-a-date') == 'not-a-date'


def test_find_date_format_issues_no_issues():
    rows = [['2024-01-01', 'foo'], ['2024-02-03', 'bar']]
    assert find_date_format_issues(rows) == []


def test_find_date_format_issues_mixed_column():
    rows = [
        ['2024-01-01', 'foo'],
        ['01/15/2024', 'bar'],
    ]
    issues = find_date_format_issues(rows)
    assert len(issues) == 1
    assert issues[0]['column'] == 0
    assert 'ISO' in issues[0]['formats_found']
    assert 'MDY' in issues[0]['formats_found']


def test_find_date_format_issues_empty_rows():
    assert find_date_format_issues([]) == []


def test_fix_dates_in_content_converts_mdy():
    rows = [['01/15/2024', 'Alice'], ['02/20/2024', 'Bob']]
    fixed, count = fix_dates_in_content(rows)
    assert fixed == [['2024-01-15', 'Alice'], ['2024-02-20', 'Bob']]
    assert count == 2


def test_fix_dates_in_content_no_changes():
    rows = [['2024-01-15', 'Alice']]
    fixed, count = fix_dates_in_content(rows)
    assert fixed == rows
    assert count == 0


def test_fix_dates_in_content_mixed():
    rows = [['01/10/2023', 'x'], ['2024-05-01', 'y']]
    fixed, count = fix_dates_in_content(rows)
    assert fixed[0][0] == '2023-01-10'
    assert fixed[1][0] == '2024-05-01'
    assert count == 1
