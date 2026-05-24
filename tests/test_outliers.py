"""Tests for csvfix/outliers.py"""

import pytest
from csvfix.outliers import (
    get_numeric_values,
    compute_iqr_bounds,
    find_outliers_in_column,
    find_outlier_issues,
)


def test_get_numeric_values_basic():
    assert get_numeric_values(["1", "2", "3"]) == [1.0, 2.0, 3.0]


def test_get_numeric_values_skips_non_numeric():
    result = get_numeric_values(["1", "abc", "3.5", ""])
    assert result == [1.0, 3.5]


def test_get_numeric_values_empty():
    assert get_numeric_values([]) == []


def test_compute_iqr_bounds_basic():
    values = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0]
    lower, upper = compute_iqr_bounds(values)
    assert lower < 1.0
    assert upper > 8.0


def test_compute_iqr_bounds_too_few_values():
    lower, upper = compute_iqr_bounds([1.0, 2.0])
    assert lower == float("-inf")
    assert upper == float("inf")


def test_find_outliers_in_column_no_outliers():
    col = ["10", "11", "12", "10", "11", "12", "10", "11"]
    assert find_outliers_in_column(col) == []


def test_find_outliers_in_column_detects_outlier():
    col = ["10", "11", "10", "11", "10", "11", "10", "1000"]
    outliers = find_outliers_in_column(col)
    assert len(outliers) == 1
    assert outliers[0][1] == "1000"


def test_find_outliers_in_column_skips_non_numeric():
    col = ["10", "11", "N/A", "10", "11", "10", "11", "1000"]
    outliers = find_outliers_in_column(col)
    assert all(v != "N/A" for _, v in outliers)


def test_find_outliers_in_column_index_is_correct():
    col = ["10", "11", "10", "11", "10", "11", "10", "999"]
    outliers = find_outliers_in_column(col)
    assert outliers[0][0] == 7


def test_find_outlier_issues_no_issues():
    content = "age,score\n25,80\n30,85\n28,82\n26,79\n31,88\n27,81\n29,84\n32,86\n"
    issues = find_outlier_issues(content)
    assert issues == []


def test_find_outlier_issues_detects_outlier():
    content = "age,score\n25,80\n30,85\n28,82\n26,79\n31,88\n27,81\n29,84\n32,9999\n"
    issues = find_outlier_issues(content)
    assert any(i["col_name"] == "score" for i in issues)
    assert any(i["value"] == "9999" for i in issues)


def test_find_outlier_issues_reports_correct_row():
    content = "val\n1\n2\n1\n2\n1\n2\n1\n500\n"
    issues = find_outlier_issues(content)
    assert len(issues) == 1
    assert issues[0]["row"] == 8


def test_find_outlier_issues_no_header():
    content = "1\n2\n1\n2\n1\n2\n1\n500\n"
    issues = find_outlier_issues(content, has_header=False)
    assert len(issues) == 1
    assert issues[0]["row"] == 7


def test_find_outlier_issues_empty_content():
    assert find_outlier_issues("") == []
