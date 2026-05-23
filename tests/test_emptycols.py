"""Tests for csvfix.emptycols module."""

import pytest
from csvfix.emptycols import (
    find_empty_columns,
    remove_empty_columns,
    find_empty_column_issues,
    fix_empty_columns_in_content,
)


# ---------------------------------------------------------------------------
# find_empty_columns
# ---------------------------------------------------------------------------

def test_find_empty_columns_no_empty():
    rows = [["a", "b", "c"], ["1", "2", "3"]]
    assert find_empty_columns(rows) == []


def test_find_empty_columns_single_empty():
    rows = [["a", "", "c"], ["1", "", "3"]]
    assert find_empty_columns(rows) == [1]


def test_find_empty_columns_multiple_empty():
    rows = [["", "b", ""], ["", "2", ""]]
    assert find_empty_columns(rows) == [0, 2]


def test_find_empty_columns_whitespace_only_counts_as_empty():
    rows = [["a", "  ", "c"], ["1", "\t", "3"]]
    assert find_empty_columns(rows) == [1]


def test_find_empty_columns_empty_rows():
    assert find_empty_columns([]) == []


def test_find_empty_columns_partial_empty_not_flagged():
    rows = [["a", "", "c"], ["1", "2", "3"]]
    assert find_empty_columns(rows) == []


# ---------------------------------------------------------------------------
# remove_empty_columns
# ---------------------------------------------------------------------------

def test_remove_empty_columns_removes_correct_index():
    rows = [["a", "", "c"], ["1", "", "3"]]
    result = remove_empty_columns(rows, [1])
    assert result == [["a", "c"], ["1", "3"]]


def test_remove_empty_columns_no_indices_unchanged():
    rows = [["a", "b"], ["1", "2"]]
    assert remove_empty_columns(rows, []) == rows


def test_remove_empty_columns_multiple_indices():
    rows = [["", "b", ""], ["", "2", ""]]
    result = remove_empty_columns(rows, [0, 2])
    assert result == [["b"], ["2"]]


# ---------------------------------------------------------------------------
# find_empty_column_issues
# ---------------------------------------------------------------------------

def test_find_empty_column_issues_structure():
    rows = [["a", "", "c"], ["1", "", "3"]]
    report = find_empty_column_issues(rows)
    assert report["empty_column_count"] == 1
    assert report["empty_column_indices"] == [1]


def test_find_empty_column_issues_no_issues():
    rows = [["a", "b"], ["1", "2"]]
    report = find_empty_column_issues(rows)
    assert report["empty_column_count"] == 0
    assert report["empty_column_indices"] == []


# ---------------------------------------------------------------------------
# fix_empty_columns_in_content
# ---------------------------------------------------------------------------

def test_fix_empty_columns_in_content_removes_empty():
    content = "name,,age\nAlice,,30\nBob,,25\n"
    fixed, count = fix_empty_columns_in_content(content)
    assert count == 1
    assert ",," not in fixed
    assert "name,age" in fixed


def test_fix_empty_columns_in_content_no_change():
    content = "name,age\nAlice,30\n"
    fixed, count = fix_empty_columns_in_content(content)
    assert count == 0
    assert fixed.strip() == content.strip()


def test_fix_empty_columns_in_content_empty_string():
    fixed, count = fix_empty_columns_in_content("")
    assert fixed == ""
    assert count == 0
