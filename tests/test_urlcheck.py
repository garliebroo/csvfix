"""Tests for csvfix.urlcheck module."""

import pytest
from csvfix.urlcheck import (
    is_valid_url,
    looks_like_url,
    find_invalid_urls,
    find_url_columns,
    find_urlcheck_issues,
)


# --- is_valid_url ---

def test_is_valid_url_basic_https():
    assert is_valid_url("https://example.com") is True


def test_is_valid_url_with_path():
    assert is_valid_url("https://example.com/path/to/page") is True


def test_is_valid_url_ftp():
    assert is_valid_url("ftp://files.example.org/data.csv") is True


def test_is_valid_url_missing_scheme():
    assert is_valid_url("www.example.com") is False


def test_is_valid_url_missing_netloc():
    assert is_valid_url("https://") is False


def test_is_valid_url_no_dot_in_netloc():
    assert is_valid_url("https://localhost") is False


def test_is_valid_url_unknown_scheme():
    assert is_valid_url("mailto:user@example.com") is False


def test_is_valid_url_empty():
    assert is_valid_url("") is False


# --- looks_like_url ---

def test_looks_like_url_http():
    assert looks_like_url("http://example.com") is True


def test_looks_like_url_www():
    assert looks_like_url("www.example.com") is True


def test_looks_like_url_plain_text():
    assert looks_like_url("just some text") is False


def test_looks_like_url_email():
    assert looks_like_url("user@example.com") is False


# --- find_invalid_urls ---

def test_find_invalid_urls_all_valid():
    rows = [["https://example.com"], ["https://other.org"]]
    assert find_invalid_urls(rows, 0) == []


def test_find_invalid_urls_detects_bad_url():
    rows = [["https://example.com"], ["http://"], ["https://good.io"]]
    issues = find_invalid_urls(rows, 0)
    assert len(issues) == 1
    assert issues[0][0] == 1  # row index
    assert issues[0][2] == "http://"


def test_find_invalid_urls_ignores_non_url_values():
    rows = [["Alice"], ["Bob"]]
    assert find_invalid_urls(rows, 0) == []


def test_find_invalid_urls_out_of_bounds_col():
    rows = [["only_one_col"]]
    assert find_invalid_urls(rows, 5) == []


# --- find_url_columns ---

def test_find_url_columns_detects_url_column():
    rows = [
        ["name", "https://a.com"],
        ["name2", "https://b.org"],
    ]
    assert 1 in find_url_columns(rows)


def test_find_url_columns_ignores_mixed_column():
    rows = [
        ["https://a.com"],
        ["not a url"],
        ["still not"],
        ["nope"],
    ]
    # Only 25% look like URLs, below default threshold of 50%
    assert find_url_columns(rows) == []


def test_find_url_columns_empty_rows():
    assert find_url_columns([]) == []


# --- find_urlcheck_issues ---

def test_find_urlcheck_issues_clean():
    rows = [["https://valid.com"], ["https://also-valid.net"]]
    report = find_urlcheck_issues(rows)
    assert report["count"] == 0
    assert report["invalid_urls"] == []


def test_find_urlcheck_issues_with_bad_url():
    rows = [["https://good.com"], ["http://"], ["https://another.io"]]
    report = find_urlcheck_issues(rows)
    assert report["count"] == 1
    assert report["url_columns"] == [0]
