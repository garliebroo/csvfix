import pytest
from csvfix.rangecheck import (
    is_in_range,
    find_out_of_range_fields,
    find_rangecheck_issues,
)


def test_is_in_range_within_bounds():
    assert is_in_range("50", 0, 100) is True


def test_is_in_range_at_min_boundary():
    assert is_in_range("0", 0, 100) is True


def test_is_in_range_at_max_boundary():
    assert is_in_range("100", 0, 100) is True


def test_is_in_range_below_min():
    assert is_in_range("-1", 0, 100) is False


def test_is_in_range_above_max():
    assert is_in_range("101", 0, 100) is False


def test_is_in_range_no_bounds():
    assert is_in_range("999999") is True


def test_is_in_range_non_numeric_skipped():
    assert is_in_range("hello", 0, 100) is True


def test_is_in_range_empty_string_skipped():
    assert is_in_range("", 0, 100) is True


def test_is_in_range_float_value():
    assert is_in_range("3.14", 0.0, 10.0) is True


def test_is_in_range_float_out_of_range():
    assert is_in_range("10.01", 0.0, 10.0) is False


def test_find_out_of_range_fields_no_issues():
    rows = [["name", "age"], ["Alice", "30"], ["Bob", "25"]]
    issues = find_out_of_range_fields(rows, column_index=1, min_val=0, max_val=120)
    assert issues == []


def test_find_out_of_range_fields_detects_issue():
    rows = [["name", "age"], ["Alice", "200"], ["Bob", "25"]]
    issues = find_out_of_range_fields(rows, column_index=1, min_val=0, max_val=120)
    assert len(issues) == 1
    assert issues[0]["row"] == 1
    assert issues[0]["value"] == "200"


def test_find_out_of_range_fields_no_header():
    rows = [["200"], ["30"]]
    issues = find_out_of_range_fields(rows, column_index=0, min_val=0, max_val=120, has_header=False)
    assert len(issues) == 1
    assert issues[0]["row"] == 0


def test_find_out_of_range_fields_skips_short_rows():
    rows = [["name", "age"], ["Alice"]]
    issues = find_out_of_range_fields(rows, column_index=1, min_val=0, max_val=120)
    assert issues == []


def test_find_rangecheck_issues_multiple_columns():
    content = "score,age\n95,25\n110,200\n50,30\n"
    issues = find_rangecheck_issues(
        content,
        column_ranges={0: (0, 100), 1: (0, 120)},
    )
    assert len(issues) == 2
    values = {i["value"] for i in issues}
    assert "110" in values
    assert "200" in values


def test_find_rangecheck_issues_empty_content():
    issues = find_rangecheck_issues("", column_ranges={0: (0, 100)})
    assert issues == []


def test_find_rangecheck_issues_only_header():
    content = "score\n"
    issues = find_rangecheck_issues(content, column_ranges={0: (0, 100)})
    assert issues == []
