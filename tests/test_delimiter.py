"""Tests for csvfix.delimiter module."""

import pytest
from csvfix.delimiter import (
    detect_delimiter,
    normalize_delimiter,
    has_inconsistent_columns,
    get_column_count_report,
)


@pytest.fixture
def comma_csv():
    return "name,age,city\nAlice,30,NYC\nBob,25,LA\n"


@pytest.fixture
def semicolon_csv():
    return "name;age;city\nAlice;30;NYC\nBob;25;LA\n"


@pytest.fixture
def tab_csv():
    return "name\tage\tcity\nAlice\t30\tNYC\nBob\t25\tLA\n"


@pytest.fixture
def inconsistent_csv():
    return "name,age,city\nAlice,30\nBob,25,LA,extra\n"


def test_detect_delimiter_comma(comma_csv):
    assert detect_delimiter(comma_csv) == ","


def test_detect_delimiter_semicolon(semicolon_csv):
    assert detect_delimiter(semicolon_csv) == ";"


def test_detect_delimiter_tab(tab_csv):
    assert detect_delimiter(tab_csv) == "\t"


def test_detect_delimiter_empty_returns_comma():
    assert detect_delimiter("") == ","


def test_normalize_delimiter_semicolon_to_comma(semicolon_csv):
    result = normalize_delimiter(semicolon_csv, target=",")
    assert ";" not in result
    assert "name,age,city" in result
    assert "Alice,30,NYC" in result


def test_normalize_delimiter_already_correct(comma_csv):
    result = normalize_delimiter(comma_csv, target=",")
    assert result == comma_csv


def test_normalize_delimiter_tab_to_pipe(tab_csv):
    result = normalize_delimiter(tab_csv, target="|")
    assert "\t" not in result
    assert "name|age|city" in result


def test_has_inconsistent_columns_true(inconsistent_csv):
    assert has_inconsistent_columns(inconsistent_csv) is True


def test_has_inconsistent_columns_false(comma_csv):
    assert has_inconsistent_columns(comma_csv) is False


def test_get_column_count_report(inconsistent_csv):
    report = get_column_count_report(inconsistent_csv)
    # header=3, Alice row=2, Bob row=4
    assert report[3] == 1
    assert report[2] == 1
    assert report[4] == 1


def test_get_column_count_report_uniform(comma_csv):
    report = get_column_count_report(comma_csv)
    assert list(report.keys()) == [3]
    assert report[3] == 3
