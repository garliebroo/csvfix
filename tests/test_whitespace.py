"""Tests for csvfix.whitespace module."""

import pytest
from csvfix.whitespace import (
    strip_field_whitespace,
    collapse_internal_whitespace,
    fix_whitespace_in_content,
    find_whitespace_issues,
)


def test_strip_field_whitespace_basic():
    row = [" Alice ", "  30", "NYC  "]
    assert strip_field_whitespace(row) == ["Alice", "30", "NYC"]


def test_strip_field_whitespace_no_change():
    row = ["Alice", "30", "NYC"]
    assert strip_field_whitespace(row) == ["Alice", "30", "NYC"]


def test_collapse_internal_whitespace():
    assert collapse_internal_whitespace("hello   world") == "hello world"


def test_collapse_internal_whitespace_tabs():
    assert collapse_internal_whitespace("foo\t\tbar") == "foo bar"


def test_collapse_internal_whitespace_no_change():
    assert collapse_internal_whitespace("hello world") == "hello world"


def test_fix_whitespace_strip_only():
    content = " name , age , city \n Alice , 30 , NYC \n"
    result = fix_whitespace_in_content(content, strip=True, collapse=False)
    assert "name,age,city" in result
    assert "Alice,30,NYC" in result


def test_fix_whitespace_collapse():
    content = 'name,bio\nAlice,"loves  cats  and  dogs"\n'
    result = fix_whitespace_in_content(content, strip=True, collapse=True)
    assert "loves cats and dogs" in result


def test_fix_whitespace_preserves_row_count():
    content = " a , b \n 1 , 2 \n 3 , 4 \n"
    result = fix_whitespace_in_content(content)
    assert len(result.strip().splitlines()) == 3


def test_find_whitespace_issues_detects_leading():
    content = "name,age\n Alice,30\n"
    issues = find_whitespace_issues(content)
    assert len(issues) == 1
    assert issues[0]["row"] == 1
    assert issues[0]["col"] == 0


def test_find_whitespace_issues_detects_double_space():
    content = "name,bio\nBob,hello  world\n"
    issues = find_whitespace_issues(content)
    assert any(i["col"] == 1 for i in issues)


def test_find_whitespace_issues_clean_content():
    content = "name,age\nAlice,30\nBob,25\n"
    assert find_whitespace_issues(content) == []
