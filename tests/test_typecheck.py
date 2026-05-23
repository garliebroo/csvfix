"""Tests for csvfix/typecheck.py"""

import pytest
from csvfix.typecheck import (
    infer_type,
    get_column_types,
    find_type_inconsistencies,
    find_typecheck_issues,
)


# --- infer_type ---

def test_infer_type_empty():
    assert infer_type("") == "empty"
    assert infer_type("   ") == "empty"


def test_infer_type_int():
    assert infer_type("42") == "int"
    assert infer_type("-7") == "int"


def test_infer_type_float():
    assert infer_type("3.14") == "float"
    assert infer_type(".5") == "float"
    assert infer_type("-0.001") == "float"


def test_infer_type_bool():
    assert infer_type("true") == "bool"
    assert infer_type("False") == "bool"
    assert infer_type("yes") == "bool"
    assert infer_type("0") == "bool"


def test_infer_type_string():
    assert infer_type("hello") == "string"
    assert infer_type("123abc") == "string"


# --- get_column_types ---

def test_get_column_types_uniform():
    rows = [["1", "alice"], ["2", "bob"], ["3", "carol"]]
    col_types = get_column_types(rows)
    assert col_types[0]["int"] == 3
    assert col_types[1]["string"] == 3


def test_get_column_types_mixed():
    rows = [["1"], ["two"], ["3"]]
    col_types = get_column_types(rows)
    assert col_types[0]["int"] == 2
    assert col_types[0]["string"] == 1


def test_get_column_types_empty_rows():
    assert get_column_types([]) == {}


# --- find_type_inconsistencies ---

def test_find_type_inconsistencies_clean():
    from collections import Counter
    col_types = {0: Counter({"int": 5}), 1: Counter({"string": 5})}
    assert find_type_inconsistencies(col_types) == []


def test_find_type_inconsistencies_mixed_with_header():
    from collections import Counter
    col_types = {0: Counter({"int": 3, "string": 1})}
    issues = find_type_inconsistencies(col_types, header=["age"])
    assert len(issues) == 1
    assert "age" in issues[0]
    assert "mixed" in issues[0]


def test_find_type_inconsistencies_ignores_empty():
    from collections import Counter
    col_types = {0: Counter({"int": 4, "empty": 2})}
    assert find_type_inconsistencies(col_types) == []


# --- find_typecheck_issues ---

def test_find_typecheck_issues_mixed_column():
    content = "name,score\nalice,95\nbob,eighty\ncarol,70\n"
    issues = find_typecheck_issues(content)
    assert any("score" in i for i in issues)


def test_find_typecheck_issues_clean():
    content = "name,score\nalice,95\nbob,80\n"
    assert find_typecheck_issues(content) == []


def test_find_typecheck_issues_empty_content():
    assert find_typecheck_issues("") == []


def test_find_typecheck_issues_no_header():
    content = "1,hello\n2,world\nthree,foo\n"
    issues = find_typecheck_issues(content, has_header=False)
    assert any("0" in i for i in issues)
