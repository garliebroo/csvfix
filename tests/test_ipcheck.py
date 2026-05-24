"""Tests for csvfix/ipcheck.py"""

import pytest
from csvfix.ipcheck import (
    is_valid_ipv4,
    is_valid_ipv6,
    is_valid_ip,
    looks_like_ip_column,
    find_ip_columns,
    find_invalid_ips,
    find_ipcheck_issues,
)


# --- is_valid_ipv4 ---

def test_is_valid_ipv4_basic():
    assert is_valid_ipv4("192.168.1.1") is True

def test_is_valid_ipv4_zeros():
    assert is_valid_ipv4("0.0.0.0") is True

def test_is_valid_ipv4_broadcast():
    assert is_valid_ipv4("255.255.255.255") is True

def test_is_valid_ipv4_out_of_range():
    assert is_valid_ipv4("256.0.0.1") is False

def test_is_valid_ipv4_too_few_octets():
    assert is_valid_ipv4("192.168.1") is False

def test_is_valid_ipv4_letters():
    assert is_valid_ipv4("abc.def.ghi.jkl") is False

def test_is_valid_ipv4_strips_whitespace():
    assert is_valid_ipv4("  10.0.0.1  ") is True


# --- is_valid_ipv6 ---

def test_is_valid_ipv6_full():
    assert is_valid_ipv6("2001:0db8:85a3:0000:0000:8a2e:0370:7334") is True

def test_is_valid_ipv6_loopback_compressed():
    assert is_valid_ipv6("::1") is True

def test_is_valid_ipv6_all_zeros():
    assert is_valid_ipv6("::") is True

def test_is_valid_ipv6_invalid():
    assert is_valid_ipv6("not-an-ip") is False


# --- is_valid_ip ---

def test_is_valid_ip_v4():
    assert is_valid_ip("10.10.10.10") is True

def test_is_valid_ip_v6():
    assert is_valid_ip("::1") is True

def test_is_valid_ip_invalid():
    assert is_valid_ip("hello") is False

def test_is_valid_ip_empty():
    assert is_valid_ip("") is False


# --- looks_like_ip_column ---

def test_looks_like_ip_column_all_valid():
    values = ["192.168.0.1", "10.0.0.1", "172.16.0.5"]
    assert looks_like_ip_column(values) is True

def test_looks_like_ip_column_mostly_valid():
    values = ["192.168.0.1", "10.0.0.1", "not-an-ip"]
    assert looks_like_ip_column(values, threshold=0.6) is True

def test_looks_like_ip_column_mostly_invalid():
    values = ["hello", "world", "foo", "192.168.0.1"]
    assert looks_like_ip_column(values) is False

def test_looks_like_ip_column_empty():
    assert looks_like_ip_column([]) is False

def test_looks_like_ip_column_skips_empty_strings():
    values = ["", "192.168.1.1", ""]
    assert looks_like_ip_column(values) is True


# --- find_invalid_ips ---

def test_find_invalid_ips_all_valid():
    rows = [["192.168.1.1"], ["10.0.0.1"]]
    header = ["ip_address"]
    assert find_invalid_ips(rows, header) == []

def test_find_invalid_ips_detects_bad():
    rows = [["192.168.1.1"], ["999.0.0.1"]]
    header = ["ip_address"]
    issues = find_invalid_ips(rows, header)
    assert len(issues) == 1
    assert issues[0][2] == "999.0.0.1"

def test_find_invalid_ips_empty_field_skipped():
    rows = [[""], ["10.0.0.1"]]
    header = ["ip"]
    assert find_invalid_ips(rows, header) == []


# --- find_ipcheck_issues ---

def test_find_ipcheck_issues_clean():
    content = "ip_address\n192.168.1.1\n10.0.0.2\n"
    assert find_ipcheck_issues(content) == []

def test_find_ipcheck_issues_reports_bad():
    content = "ip_address\n192.168.1.1\n999.999.999.999\n"
    issues = find_ipcheck_issues(content)
    assert len(issues) == 1
    assert "999.999.999.999" in issues[0]
    assert "ip_address" in issues[0]

def test_find_ipcheck_issues_empty_content():
    assert find_ipcheck_issues("") == []
