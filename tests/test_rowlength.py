"""Tests for csvfix.rowlength module."""

import pytest
from csvfix.rowlength import (
    get_expected_column_count,
    find_short_rows,
    find_long_rows,
    pad_short_rows,
    truncate_long_rows,
    find_rowlength_issues,
)


@pytest.fixture
def uniform_rows():
    return [["a", "b", "c"], ["1", "2", "3"], ["x", "y", "z"]]


@pytest.fixture
def mixed_rows():
    return [["a", "b", "c"], ["1", "2"], ["x", "y", "z", "w"]]


def test_get_expected_column_count_uniform(uniform_rows):
    assert get_expected_column_count(uniform_rows) == 3


def test_get_expected_column_count_empty():
    assert get_expected_column_count([]) == 0


def test_get_expected_column_count_mixed(mixed_rows):
    # two rows have 3 cols, one has 2, one has 4 — 3 wins
    rows = [["a", "b", "c"], ["1", "2", "3"], ["x", "y"], ["p", "q", "r", "s"]]
    assert get_expected_column_count(rows) == 3


def test_find_short_rows_none(uniform_rows):
    assert find_short_rows(uniform_rows) == []


def test_find_short_rows_detects(mixed_rows):
    result = find_short_rows(mixed_rows, expected=3)
    assert (1, 2) in result


def test_find_long_rows_none(uniform_rows):
    assert find_long_rows(uniform_rows) == []


def test_find_long_rows_detects(mixed_rows):
    result = find_long_rows(mixed_rows, expected=3)
    assert (2, 4) in result


def test_pad_short_rows_no_change(uniform_rows):
    result = pad_short_rows(uniform_rows, expected=3)
    assert result == uniform_rows


def test_pad_short_rows_fills_empty():
    rows = [["a", "b", "c"], ["1", "2"]]
    result = pad_short_rows(rows, expected=3)
    assert result[1] == ["1", "2", ""]


def test_pad_short_rows_custom_fill():
    rows = [["a", "b", "c"], ["x"]]
    result = pad_short_rows(rows, expected=3, fill="N/A")
    assert result[1] == ["x", "N/A", "N/A"]


def test_truncate_long_rows_no_change(uniform_rows):
    result = truncate_long_rows(uniform_rows, expected=3)
    assert result == uniform_rows


def test_truncate_long_rows_cuts():
    rows = [["a", "b", "c"], ["1", "2", "3", "4"]]
    result = truncate_long_rows(rows, expected=3)
    assert result[1] == ["1", "2", "3"]


def test_find_rowlength_issues_clean(uniform_rows):
    report = find_rowlength_issues(uniform_rows)
    assert report["total_issues"] == 0
    assert report["expected_columns"] == 3


def test_find_rowlength_issues_mixed(mixed_rows):
    report = find_rowlength_issues(mixed_rows)
    assert report["total_issues"] == 2
    assert len(report["short_rows"]) == 1
    assert len(report["long_rows"]) == 1
