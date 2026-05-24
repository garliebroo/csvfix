"""Tests for csvfix.emailcheck module."""

import pytest
from csvfix.emailcheck import (
    is_valid_email,
    looks_like_email,
    find_invalid_emails,
    find_email_columns,
    find_emailcheck_issues,
)


# --- is_valid_email ---

def test_is_valid_email_basic():
    assert is_valid_email('user@example.com') is True


def test_is_valid_email_subdomain():
    assert is_valid_email('user@mail.example.co.uk') is True


def test_is_valid_email_plus_tag():
    assert is_valid_email('user+tag@example.org') is True


def test_is_valid_email_missing_at():
    assert is_valid_email('userexample.com') is False


def test_is_valid_email_missing_domain():
    assert is_valid_email('user@') is False


def test_is_valid_email_missing_tld():
    assert is_valid_email('user@example') is False


def test_is_valid_email_double_at():
    assert is_valid_email('user@@example.com') is False


def test_is_valid_email_with_spaces():
    # strip should handle leading/trailing spaces
    assert is_valid_email('  user@example.com  ') is True


# --- looks_like_email ---

def test_looks_like_email_true():
    assert looks_like_email('bad@broken') is True


def test_looks_like_email_false():
    assert looks_like_email('plaintext') is False


# --- find_invalid_emails ---

def test_find_invalid_emails_no_issues():
    rows = [['name', 'email'], ['Alice', 'alice@example.com']]
    assert find_invalid_emails(rows, col_index=1) == []


def test_find_invalid_emails_detects_bad():
    rows = [['name', 'email'], ['Bob', 'bob@'], ['Alice', 'alice@example.com']]
    issues = find_invalid_emails(rows, col_index=1)
    assert len(issues) == 1
    assert issues[0][2] == 'bob@'


def test_find_invalid_emails_skips_non_email_fields():
    rows = [['name', 'email'], ['Charlie', 'just-a-name']]
    assert find_invalid_emails(rows, col_index=1) == []


def test_find_invalid_emails_no_header():
    rows = [['bad@'], ['good@example.com']]
    issues = find_invalid_emails(rows, col_index=0, has_header=False)
    assert len(issues) == 1


# --- find_email_columns ---

def test_find_email_columns_by_header_name():
    rows = [['id', 'email', 'name'], ['1', 'a@b.com', 'Alice']]
    assert find_email_columns(rows) == [1]


def test_find_email_columns_by_content():
    rows = [['id', 'contact'], ['1', 'a@b.com'], ['2', 'c@d.org']]
    assert 1 in find_email_columns(rows)


def test_find_email_columns_empty():
    assert find_email_columns([]) == []


# --- find_emailcheck_issues ---

def test_find_emailcheck_issues_clean():
    content = 'name,email\nAlice,alice@example.com\nBob,bob@example.org\n'
    report = find_emailcheck_issues(content)
    assert report['count'] == 0


def test_find_emailcheck_issues_with_bad_email():
    content = 'name,email\nAlice,not-an-email@\nBob,bob@example.org\n'
    report = find_emailcheck_issues(content)
    assert report['count'] == 1
    assert report['invalid_emails'][0][2] == 'not-an-email@'


def test_find_emailcheck_issues_reports_email_columns():
    content = 'name,email\nAlice,alice@example.com\n'
    report = find_emailcheck_issues(content)
    assert 1 in report['email_columns']
