"""Tests for csvfix/nulls.py"""

import pytest
from csvfix.nulls import (
    is_null_like,
    normalize_null,
    fix_nulls_in_row,
    find_null_issues,
    fix_nulls_in_content,
)


def test_is_null_like_empty():
    assert is_null_like("") is True


def test_is_null_like_whitespace_only():
    assert is_null_like("   ") is True


def test_is_null_like_null_string():
    assert is_null_like("NULL") is True
    assert is_null_like("null") is True
    assert is_null_like("None") is True
    assert is_null_like("NA") is True
    assert is_null_like("N/A") is True
    assert is_null_like("nil") is True
    assert is_null_like("-") is True


def test_is_null_like_normal_value():
    assert is_null_like("hello") is False
    assert is_null_like("0") is False
    assert is_null_like("false") is False


def test_is_null_like_custom_nulls():
    assert is_null_like("missing", custom_nulls=["missing", "unknown"]) is True
    assert is_null_like("unknown", custom_nulls=["missing", "unknown"]) is True
    assert is_null_like("hello", custom_nulls=["missing"]) is False


def test_normalize_null_replaces_null():
    assert normalize_null("NULL") == ""
    assert normalize_null("N/A", replacement="?") == "?"


def test_normalize_null_keeps_normal_value():
    assert normalize_null("hello") == "hello"
    assert normalize_null("42") == "42"


def test_fix_nulls_in_row_basic():
    row = ["Alice", "NULL", "30"]
    fixed, count = fix_nulls_in_row(row)
    assert fixed == ["Alice", "", "30"]
    assert count == 1


def test_fix_nulls_in_row_no_changes():
    row = ["Alice", "Smith", "30"]
    fixed, count = fix_nulls_in_row(row)
    assert fixed == ["Alice", "Smith", "30"]
    assert count == 0


def test_fix_nulls_in_row_multiple():
    row = ["N/A", "none", "active"]
    fixed, count = fix_nulls_in_row(row)
    assert fixed == ["", "", "active"]
    assert count == 2


def test_find_null_issues_reports_positions():
    content = "name,age,city\nAlice,NULL,Paris\nBob,25,N/A\n"
    issues = find_null_issues(content)
    assert len(issues) == 2
    assert issues[0]["row"] == 1
    assert issues[0]["col"] == 1
    assert issues[1]["row"] == 2
    assert issues[1]["col"] == 2


def test_find_null_issues_clean_content():
    content = "name,age\nAlice,30\nBob,25\n"
    issues = find_null_issues(content)
    assert issues == []


def test_fix_nulls_in_content():
    content = "name,score\nAlice,NULL\nBob,95\n"
    fixed, count = fix_nulls_in_content(content)
    assert count == 1
    assert "NULL" not in fixed
    assert "Alice" in fixed


def test_fix_nulls_in_content_custom_replacement():
    content = "a,b\nNone,1\n"
    fixed, count = fix_nulls_in_content(content, replacement="N/A")
    assert "N/A" in fixed
    assert count == 1
