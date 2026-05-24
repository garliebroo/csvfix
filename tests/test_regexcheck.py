import pytest
from csvfix.regexcheck import (
    is_valid_pattern,
    looks_like_pattern_column,
    find_invalid_pattern_fields,
    find_regexcheck_issues,
)


def test_is_valid_pattern_match():
    assert is_valid_pattern("ABC123", r"[A-Z]{3}\d{3}") is True


def test_is_valid_pattern_no_match():
    assert is_valid_pattern("abc123", r"[A-Z]{3}\d{3}") is False


def test_is_valid_pattern_partial_does_not_match():
    # fullmatch requires entire string to match
    assert is_valid_pattern("ABC123extra", r"[A-Z]{3}\d{3}") is False


def test_is_valid_pattern_invalid_regex_returns_false():
    assert is_valid_pattern("anything", r"[invalid") is False


def test_looks_like_pattern_column_mostly_matching():
    values = ["123-45-6789", "987-65-4321", "111-22-3333", "not-a-ssn"]
    assert looks_like_pattern_column(values, r"\d{3}-\d{2}-\d{4}") is True


def test_looks_like_pattern_column_mostly_not_matching():
    values = ["hello", "world", "foo", "123-45-6789"]
    assert looks_like_pattern_column(values, r"\d{3}-\d{2}-\d{4}") is False


def test_looks_like_pattern_column_empty_list():
    assert looks_like_pattern_column([], r"\d+") is False


def test_looks_like_pattern_column_all_empty_strings():
    assert looks_like_pattern_column(["", "  ", ""], r"\d+") is False


def test_find_invalid_pattern_fields_no_issues():
    rows = [["Alice", "123"], ["Bob", "456"]]
    issues = find_invalid_pattern_fields(rows, col_index=1, pattern=r"\d+")
    assert issues == []


def test_find_invalid_pattern_fields_finds_bad_value():
    rows = [["Alice", "123"], ["Bob", "abc"]]
    issues = find_invalid_pattern_fields(rows, col_index=1, pattern=r"\d+")
    assert len(issues) == 1
    assert issues[0]["row"] == 1
    assert issues[0]["value"] == "abc"


def test_find_invalid_pattern_fields_skips_empty_by_default():
    rows = [["Alice", ""], ["Bob", "abc"]]
    issues = find_invalid_pattern_fields(rows, col_index=1, pattern=r"\d+")
    assert all(i["value"] != "" for i in issues)


def test_find_invalid_pattern_fields_includes_empty_when_flag_off():
    rows = [["Alice", ""]]
    issues = find_invalid_pattern_fields(rows, col_index=1, pattern=r"\d+", skip_empty=False)
    assert len(issues) == 1


def test_find_invalid_pattern_fields_col_out_of_range():
    rows = [["only_one_col"]]
    issues = find_invalid_pattern_fields(rows, col_index=5, pattern=r"\d+")
    assert issues == []


def test_find_regexcheck_issues_basic():
    content = "name,code\nAlice,A01\nBob,999\nCarol,B02"
    issues = find_regexcheck_issues(content, column_patterns={1: r"[A-Z]\d{2}"}, has_header=True)
    assert len(issues) == 1
    assert issues[0]["value"] == "999"
    assert issues[0]["row"] == 2  # 0-based, header is row 0


def test_find_regexcheck_issues_no_header():
    content = "Alice,A01\nBob,999"
    issues = find_regexcheck_issues(content, column_patterns={1: r"[A-Z]\d{2}"}, has_header=False)
    assert len(issues) == 1
    assert issues[0]["row"] == 1


def test_find_regexcheck_issues_empty_content():
    issues = find_regexcheck_issues("", column_patterns={0: r"\d+"})
    assert issues == []


def test_find_regexcheck_issues_multiple_columns():
    content = "zip,code\n12345,A01\nBAD,999"
    issues = find_regexcheck_issues(
        content,
        column_patterns={0: r"\d{5}", 1: r"[A-Z]\d{2}"},
        has_header=True,
    )
    assert len(issues) == 2
