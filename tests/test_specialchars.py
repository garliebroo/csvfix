"""Tests for csvfix.specialchars module."""

import pytest
from csvfix.specialchars import (
    find_control_chars,
    find_invisible_chars,
    strip_special_chars,
    fix_special_chars_in_row,
    find_specialchar_issues,
    fix_specialchars_in_content,
)


def test_find_control_chars_clean():
    assert find_control_chars("hello world") == []


def test_find_control_chars_null_byte():
    assert find_control_chars("hel\x00lo") == ["\x00"]


def test_find_control_chars_multiple():
    result = find_control_chars("a\x01b\x1fc")
    assert "\x01" in result
    assert "\x1f" in result


def test_find_control_chars_allows_tab_newline():
    # \t (0x09), \n (0x0a), \r (0x0d) should NOT be flagged
    assert find_control_chars("col1\tcol2") == []
    assert find_control_chars("line1\nline2") == []


def test_find_invisible_chars_clean():
    assert find_invisible_chars("normal text") == []


def test_find_invisible_chars_zero_width_space():
    result = find_invisible_chars("hello\u200bworld")
    assert "\u200b" in result


def test_find_invisible_chars_soft_hyphen():
    result = find_invisible_chars("re\u00adsume")
    assert "\u00ad" in result


def test_strip_special_chars_removes_control():
    assert strip_special_chars("hel\x00lo") == "hello"


def test_strip_special_chars_removes_invisible():
    assert strip_special_chars("hi\u200bthere") == "hithere"


def test_strip_special_chars_with_replacement():
    result = strip_special_chars("a\x01b", replacement="?")
    assert result == "a?b"


def test_strip_special_chars_clean_field_unchanged():
    assert strip_special_chars("clean field") == "clean field"


def test_fix_special_chars_in_row_no_issues():
    row = ["name", "value", "123"]
    fixed, count = fix_special_chars_in_row(row)
    assert fixed == row
    assert count == 0


def test_fix_special_chars_in_row_with_issues():
    row = ["na\x00me", "ok", "val\u200b"]
    fixed, count = fix_special_chars_in_row(row)
    assert fixed == ["name", "ok", "val"]
    assert count == 2


def test_find_specialchar_issues_no_issues():
    rows = [["a", "b"], ["1", "2"]]
    assert find_specialchar_issues(rows) == []


def test_find_specialchar_issues_detects_problem():
    rows = [["header", "val\x1f"], ["1", "2"]]
    issues = find_specialchar_issues(rows)
    assert len(issues) == 1
    assert issues[0]["row"] == 0
    assert issues[0]["col"] == 1


def test_find_specialchar_issues_reports_char_types():
    rows = [["a\x00b", "c\u200bd"]]
    issues = find_specialchar_issues(rows)
    assert len(issues) == 2
    assert issues[0]["control_chars"] == ["\x00"]
    assert issues[1]["invisible_chars"] == ["\u200b"]


def test_fix_specialchars_in_content():
    rows = [["ok", "bad\x01"], ["\u200bhidden", "fine"]]
    fixed_rows, total = fix_specialchars_in_content(rows)
    assert fixed_rows == [["ok", "bad"], ["hidden", "fine"]]
    assert total == 2
