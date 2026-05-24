"""Tests for csvfix/fieldlength.py"""

import pytest
from csvfix.fieldlength import (
    find_long_fields,
    truncate_long_fields,
    get_field_length_report,
    find_fieldlength_issues,
    DEFAULT_MAX_FIELD_LENGTH,
)


SHORT_ROWS = [["hello", "world"], ["foo", "bar"]]
LONG_ROWS = [["hello", "x" * 200], ["y" * 150, "ok"]]


def test_find_long_fields_no_issues():
    result = find_long_fields(SHORT_ROWS, max_length=50)
    assert result == []


def test_find_long_fields_detects_long_field():
    result = find_long_fields(LONG_ROWS, max_length=100)
    assert (0, 1, 200) in result
    assert (1, 0, 150) in result


def test_find_long_fields_exact_boundary_is_ok():
    rows = [["a" * 10]]
    result = find_long_fields(rows, max_length=10)
    assert result == []


def test_find_long_fields_one_over_boundary():
    rows = [["a" * 11]]
    result = find_long_fields(rows, max_length=10)
    assert len(result) == 1
    assert result[0][2] == 11


def test_find_long_fields_use_bytes():
    # each emoji is 4 bytes in utf-8
    rows = [["\U0001F600" * 3]]  # 3 chars but 12 bytes
    result_chars = find_long_fields(rows, max_length=5, use_bytes=False)
    result_bytes = find_long_fields(rows, max_length=5, use_bytes=True)
    assert result_chars == []  # 3 chars <= 5
    assert len(result_bytes) == 1  # 12 bytes > 5


def test_truncate_long_fields_no_change():
    result, count = truncate_long_fields(SHORT_ROWS, max_length=50)
    assert count == 0
    assert result == SHORT_ROWS


def test_truncate_long_fields_truncates():
    rows = [["a" * 20]]
    result, count = truncate_long_fields(rows, max_length=10)
    assert count == 1
    assert result[0][0] == "a" * 10


def test_truncate_long_fields_with_suffix():
    rows = [["abcdefghij" + "x" * 10]]
    result, count = truncate_long_fields(rows, max_length=10, suffix="...")
    assert count == 1
    assert result[0][0] == "abcdefg..."
    assert len(result[0][0]) == 10


def test_truncate_long_fields_multiple_rows():
    rows = [["a" * 50, "short"], ["b" * 60, "ok"]]
    result, count = truncate_long_fields(rows, max_length=20)
    assert count == 2
    assert len(result[0][0]) == 20
    assert len(result[1][0]) == 20
    assert result[0][1] == "short"


def test_get_field_length_report_empty():
    assert get_field_length_report([]) == {}


def test_get_field_length_report_basic():
    rows = [["hi", "hello"], ["a", "world"]]
    report = get_field_length_report(rows)
    assert report[0]["min"] == 1
    assert report[0]["max"] == 2
    assert report[1]["min"] == 5
    assert report[1]["max"] == 5


def test_find_fieldlength_issues_clean():
    content = "name,value\nfoo,bar\n"
    issues = find_fieldlength_issues(content, max_length=100)
    assert issues == []


def test_find_fieldlength_issues_detects_long():
    long_val = "x" * 200
    content = f"name,value\nfoo,{long_val}\n"
    issues = find_fieldlength_issues(content, max_length=100)
    assert len(issues) == 1
    assert "200" in issues[0]
    assert "100" in issues[0]
