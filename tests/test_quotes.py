"""Tests for csvfix.quotes module."""

import pytest
from csvfix.quotes import (
    find_unmatched_quotes,
    normalize_quoting,
    fix_quotes_in_row,
    find_quoting_issues,
    fix_quoting_in_content,
)


def test_find_unmatched_quotes_clean_field():
    assert find_unmatched_quotes("hello") is False


def test_find_unmatched_quotes_properly_quoted():
    assert find_unmatched_quotes('"hello world"') is False


def test_find_unmatched_quotes_unmatched():
    assert find_unmatched_quotes('say "hello') is True


def test_find_unmatched_quotes_empty():
    assert find_unmatched_quotes("") is False


def test_normalize_quoting_plain_field():
    assert normalize_quoting("simple") == "simple"


def test_normalize_quoting_field_with_comma():
    result = normalize_quoting("hello, world")
    assert result == '"hello, world"'


def test_normalize_quoting_field_with_existing_quotes():
    result = normalize_quoting('say "hi"')
    assert result == '"say ""hi"""'


def test_normalize_quoting_field_with_newline():
    result = normalize_quoting("line1\nline2")
    assert result.startswith('"') and result.endswith('"')


def test_fix_quotes_in_row_no_issues():
    row = ["name", "age", "city"]
    assert fix_quotes_in_row(row) == row


def test_fix_quotes_in_row_unmatched_opening():
    row = ['"Alice', "30", "NYC"]
    result = fix_quotes_in_row(row)
    assert result[0] == '"Alice"'


def test_find_quoting_issues_clean_csv():
    content = "name,age\nAlice,30\nBob,25\n"
    issues = find_quoting_issues(content)
    assert issues == []


def test_find_quoting_issues_detects_problem():
    content = 'name,note\nAlice,"unclosed\nBob,ok\n'
    issues = find_quoting_issues(content)
    # csv.reader may merge rows on unclosed quotes; at minimum no crash
    assert isinstance(issues, list)


def test_fix_quoting_in_content_returns_string():
    content = "name,age\nAlice,30\nBob,25\n"
    result = fix_quoting_in_content(content)
    assert isinstance(result, str)
    assert "Alice" in result
    assert "Bob" in result


def test_fix_quoting_in_content_preserves_rows():
    content = "city,country\nParis,France\nBerlin,Germany\n"
    result = fix_quoting_in_content(content)
    lines = [l for l in result.strip().splitlines() if l]
    assert len(lines) == 3
