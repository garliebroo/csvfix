"""Tests for csvfix/duplicates.py"""

import pytest
from csvfix.duplicates import (
    find_duplicate_rows,
    remove_duplicate_rows,
    find_duplicate_keys,
    find_duplicate_issues,
    fix_duplicates_in_content,
)


# --- find_duplicate_rows ---

def test_find_duplicate_rows_no_duplicates():
    rows = [["a", "1"], ["b", "2"], ["c", "3"]]
    assert find_duplicate_rows(rows) == []


def test_find_duplicate_rows_single_duplicate():
    rows = [["a", "1"], ["b", "2"], ["a", "1"]]
    assert find_duplicate_rows(rows) == [2]


def test_find_duplicate_rows_multiple_duplicates():
    rows = [["x"], ["x"], ["y"], ["x"]]
    assert find_duplicate_rows(rows) == [1, 3]


def test_find_duplicate_rows_empty():
    assert find_duplicate_rows([]) == []


# --- remove_duplicate_rows ---

def test_remove_duplicate_rows_keeps_first():
    rows = [["a", "1"], ["b", "2"], ["a", "1"]]
    result = remove_duplicate_rows(rows)
    assert result == [["a", "1"], ["b", "2"]]


def test_remove_duplicate_rows_no_change():
    rows = [["a"], ["b"], ["c"]]
    assert remove_duplicate_rows(rows) == rows


def test_remove_duplicate_rows_all_same():
    rows = [["z", "9"]] * 4
    assert remove_duplicate_rows(rows) == [["z", "9"]]


# --- find_duplicate_keys ---

def test_find_duplicate_keys_detects_dupes():
    rows = [["1", "alice"], ["2", "bob"], ["1", "charlie"]]
    result = find_duplicate_keys(rows, key_column=0)
    assert (0, "1") in result
    assert (2, "1") in result


def test_find_duplicate_keys_no_dupes():
    rows = [["1", "alice"], ["2", "bob"]]
    assert find_duplicate_keys(rows, key_column=0) == []


def test_find_duplicate_keys_out_of_bounds_column():
    rows = [["a"], ["b"]]
    assert find_duplicate_keys(rows, key_column=5) == []


# --- find_duplicate_issues ---

def test_find_duplicate_issues_reports_duplicates():
    content = "name,age\nalice,30\nbob,25\nalice,30\n"
    issues = find_duplicate_issues(content)
    assert len(issues) == 1
    assert "duplicate" in issues[0].lower()


def test_find_duplicate_issues_clean_csv():
    content = "name,age\nalice,30\nbob,25\n"
    assert find_duplicate_issues(content) == []


def test_find_duplicate_issues_empty_content():
    assert find_duplicate_issues("") == []


# --- fix_duplicates_in_content ---

def test_fix_duplicates_in_content_removes_dupes():
    content = "a,b\n1,2\n1,2\n3,4\n"
    fixed, removed = fix_duplicates_in_content(content)
    assert removed == 1
    assert fixed.count("1,2") == 1


def test_fix_duplicates_in_content_no_dupes():
    content = "a,b\n1,2\n3,4\n"
    fixed, removed = fix_duplicates_in_content(content)
    assert removed == 0
    assert "1,2" in fixed
    assert "3,4" in fixed
