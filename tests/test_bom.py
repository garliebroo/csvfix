"""Tests for csvfix.bom module."""

from csvfix.bom import (
    detect_bom,
    strip_bom,
    has_bom,
    strip_bom_from_string,
    find_bom_issues,
    BOM_UTF8,
    BOM_UTF16_LE,
    BOM_UTF16_BE,
)


def test_detect_bom_utf8():
    data = BOM_UTF8 + b"a,b,c\n"
    bom, encoding = detect_bom(data)
    assert bom == BOM_UTF8
    assert encoding == "utf-8-sig"


def test_detect_bom_utf16_le():
    data = BOM_UTF16_LE + b"\x61\x00"
    bom, encoding = detect_bom(data)
    assert bom == BOM_UTF16_LE
    assert "utf-16" in encoding


def test_detect_bom_utf16_be():
    data = BOM_UTF16_BE + b"\x00\x61"
    bom, encoding = detect_bom(data)
    assert bom == BOM_UTF16_BE
    assert "utf-16" in encoding


def test_detect_bom_none():
    data = b"a,b,c\n"
    bom, encoding = detect_bom(data)
    assert bom is None
    assert encoding is None


def test_strip_bom_removes_utf8_bom():
    data = BOM_UTF8 + b"hello,world"
    stripped, encoding = strip_bom(data)
    assert stripped == b"hello,world"
    assert encoding == "utf-8-sig"


def test_strip_bom_no_bom():
    data = b"hello,world"
    stripped, encoding = strip_bom(data)
    assert stripped == b"hello,world"
    assert encoding is None


def test_has_bom_true():
    assert has_bom(BOM_UTF8 + b"data") is True


def test_has_bom_false():
    assert has_bom(b"data") is False


def test_strip_bom_from_string_with_bom():
    text = "\ufeffname,value\n"
    result = strip_bom_from_string(text)
    assert result == "name,value\n"
    assert not result.startswith("\ufeff")


def test_strip_bom_from_string_no_bom():
    text = "name,value\n"
    result = strip_bom_from_string(text)
    assert result == "name,value\n"


def test_find_bom_issues_with_bom():
    data = BOM_UTF8 + b"a,b\n"
    issues = find_bom_issues(data)
    assert len(issues) == 1
    assert issues[0]["type"] == "bom_detected"
    assert issues[0]["severity"] == "warning"
    assert "utf-8-sig" in issues[0]["message"]


def test_find_bom_issues_clean():
    data = b"a,b\n"
    issues = find_bom_issues(data)
    assert issues == []
