"""Tests for csvfix.lineendings module."""

import pytest
from csvfix.lineendings import (
    LineEnding,
    detect_line_ending,
    normalize_line_endings,
    find_line_ending_issues,
)


def test_detect_lf():
    content = "a,b,c\nd,e,f\ng,h,i\n"
    assert detect_line_ending(content) == LineEnding.LF


def test_detect_crlf():
    content = "a,b,c\r\nd,e,f\r\ng,h,i\r\n"
    assert detect_line_ending(content) == LineEnding.CRLF


def test_detect_cr():
    content = "a,b,c\rd,e,f\rg,h,i\r"
    assert detect_line_ending(content) == LineEnding.CR


def test_detect_mixed():
    content = "a,b,c\r\nd,e,f\ng,h,i\r"
    assert detect_line_ending(content) == LineEnding.MIXED


def test_detect_empty_defaults_to_lf():
    assert detect_line_ending("") == LineEnding.LF


def test_normalize_crlf_to_lf():
    content = "a,b\r\nc,d\r\n"
    result = normalize_line_endings(content, LineEnding.LF)
    assert result == "a,b\nc,d\n"
    assert "\r" not in result


def test_normalize_lf_to_crlf():
    content = "a,b\nc,d\n"
    result = normalize_line_endings(content, LineEnding.CRLF)
    assert result == "a,b\r\nc,d\r\n"


def test_normalize_cr_to_lf():
    content = "a,b\rc,d\r"
    result = normalize_line_endings(content, LineEnding.LF)
    assert result == "a,b\nc,d\n"


def test_normalize_mixed_to_lf():
    content = "a,b\r\nc,d\re,f\n"
    result = normalize_line_endings(content, LineEnding.LF)
    assert "\r" not in result
    assert result.count("\n") == 3


def test_normalize_raises_on_mixed_target():
    with pytest.raises(ValueError, match="mixed"):
        normalize_line_endings("a,b\n", LineEnding.MIXED)


def test_find_issues_clean_lf():
    content = "a,b\nc,d\n"
    issues = find_line_ending_issues(content)
    assert issues == []


def test_find_issues_mixed():
    content = "a,b\r\nc,d\n"
    issues = find_line_ending_issues(content)
    assert len(issues) == 1
    assert issues[0]["type"] == "mixed_line_endings"
    assert issues[0]["severity"] == "warning"


def test_find_issues_crlf():
    content = "a,b\r\nc,d\r\n"
    issues = find_line_ending_issues(content)
    assert len(issues) == 1
    assert issues[0]["type"] == "crlf_line_endings"
    assert issues[0]["severity"] == "info"


def test_find_issues_cr_only():
    content = "a,b\rc,d\r"
    issues = find_line_ending_issues(content)
    assert len(issues) == 1
    assert issues[0]["type"] == "cr_line_endings"
