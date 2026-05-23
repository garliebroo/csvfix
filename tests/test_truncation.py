"""Tests for csvfix.truncation module."""

import pytest
from csvfix.truncation import (
    find_truncated_fields,
    get_field_length_stats,
    find_truncation_issues,
    DEFAULT_MAX_FIELD_LENGTH,
)


@pytest.fixture
def short_rows():
    return [["name", "email"], ["Alice", "alice@example.com"], ["Bob", "bob@example.com"]]


@pytest.fixture
def long_rows():
    long_val = "x" * 255
    return [["name", "bio"], ["Alice", long_val], ["Bob", "short"]]


def test_find_truncated_fields_no_issues(short_rows):
    issues = find_truncated_fields(short_rows)
    assert issues == []


def test_find_truncated_fields_detects_max_length(long_rows):
    issues = find_truncated_fields(long_rows, max_length=255)
    assert len(issues) == 1
    assert issues[0]["row"] == 1
    assert issues[0]["col"] == 1
    assert issues[0]["col_name"] == "bio"
    assert issues[0]["length"] == 255


def test_find_truncated_fields_custom_max():
    rows = [["id", "label"], ["1", "hello world"]]
    issues = find_truncated_fields(rows, max_length=10)
    assert len(issues) == 1
    assert issues[0]["col_name"] == "label"


def test_find_truncated_fields_no_header():
    rows = [["x" * 50], ["short"]]
    issues = find_truncated_fields(rows, max_length=40, has_header=False)
    assert len(issues) == 1
    assert issues[0]["col_name"] == "0"


def test_find_truncated_fields_value_preview_truncated():
    rows = [["note"], ["a" * 100]]
    issues = find_truncated_fields(rows, max_length=50)
    assert issues[0]["value_preview"].endswith("...")
    assert len(issues[0]["value_preview"]) == 43  # 40 + len("...")


def test_find_truncated_fields_value_preview_short():
    rows = [["note"], ["hello" * 10]]
    issues = find_truncated_fields(rows, max_length=10)
    assert not issues[0]["value_preview"].endswith("...")


def test_get_field_length_stats_basic(short_rows):
    stats = get_field_length_stats(short_rows)
    assert "name" in stats
    assert "email" in stats
    assert stats["name"]["max"] == 5  # "Alice"
    assert stats["name"]["count"] == 2


def test_get_field_length_stats_no_header():
    rows = [["abc", "de"], ["f", "ghij"]]
    stats = get_field_length_stats(rows, has_header=False)
    assert "0" in stats
    assert "1" in stats
    assert stats["0"]["max"] == 3


def test_find_truncation_issues_from_content():
    long_val = "z" * 100
    content = f"name,value\nAlice,{long_val}\nBob,short\n"
    issues = find_truncation_issues(content, max_length=50)
    assert len(issues) == 1
    assert issues[0]["col_name"] == "value"


def test_find_truncation_issues_no_issues():
    content = "name,value\nAlice,hello\nBob,world\n"
    issues = find_truncation_issues(content)
    assert issues == []


def test_default_max_field_length():
    assert DEFAULT_MAX_FIELD_LENGTH == 255
