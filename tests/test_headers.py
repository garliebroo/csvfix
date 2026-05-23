import pytest
from csvfix.headers import (
    detect_header_row,
    find_duplicate_headers,
    normalize_header_names,
    find_header_issues,
    fix_headers_in_content,
)


def test_detect_header_row_true():
    rows = [["name", "age", "city"], ["Alice", "30", "NYC"]]
    assert detect_header_row(rows) is True


def test_detect_header_row_false_all_numeric():
    rows = [["1", "2", "3"], ["4", "5", "6"]]
    assert detect_header_row(rows) is False


def test_detect_header_row_empty():
    assert detect_header_row([]) is False


def test_detect_header_row_mixed_numeric():
    # has at least one numeric value in first row
    rows = [["name", "42", "city"]]
    assert detect_header_row(rows) is False


def test_find_duplicate_headers_no_dupes():
    assert find_duplicate_headers(["name", "age", "city"]) == []


def test_find_duplicate_headers_with_dupe():
    result = find_duplicate_headers(["name", "age", "name"])
    assert len(result) == 1
    assert result[0][0] == "name"
    assert set(result[0][1]) == {0, 2}


def test_find_duplicate_headers_case_insensitive():
    result = find_duplicate_headers(["Name", "AGE", "name"])
    assert len(result) == 1
    assert result[0][0] == "name"


def test_normalize_header_names_basic():
    result = normalize_header_names(["First Name", "Last Name", "Age"])
    assert result == ["first_name", "last_name", "age"]


def test_normalize_header_names_strips_whitespace():
    result = normalize_header_names(["  name  ", " age"])
    assert result == ["name", "age"]


def test_find_header_issues_no_issues():
    content = "name,age,city\nAlice,30,NYC\n"
    issues = find_header_issues(content)
    assert issues == []


def test_find_header_issues_duplicate_header():
    content = "name,age,name\nAlice,30,NYC\n"
    issues = find_header_issues(content)
    assert any("duplicate" in i.lower() for i in issues)


def test_find_header_issues_whitespace_header():
    content = "name, age ,city\nAlice,30,NYC\n"
    issues = find_header_issues(content)
    assert any("whitespace" in i.lower() for i in issues)


def test_find_header_issues_empty_content():
    assert find_header_issues("") == []


def test_fix_headers_in_content_normalizes():
    content = "First Name,Last Name,Age\nAlice,Smith,30\n"
    fixed, count = fix_headers_in_content(content)
    assert "first_name" in fixed
    assert "last_name" in fixed
    assert count == 2


def test_fix_headers_in_content_no_changes_needed():
    content = "name,age,city\nAlice,30,NYC\n"
    fixed, count = fix_headers_in_content(content)
    assert count == 0


def test_fix_headers_in_content_empty():
    fixed, count = fix_headers_in_content("")
    assert fixed == ""
    assert count == 0
