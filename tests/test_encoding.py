"""Tests for csvfix.encoding module."""

import os
import tempfile
import pytest

from csvfix.encoding import (
    detect_encoding,
    fix_encoding,
    read_with_encoding,
    write_fixed_file,
    FALLBACK_ENCODING,
)


@pytest.fixture
def utf8_csv(tmp_path):
    f = tmp_path / "sample_utf8.csv"
    f.write_bytes("name,city\nAlice,São Paulo\nBob,München\n".encode("utf-8"))
    return str(f)


@pytest.fixture
def latin1_csv(tmp_path):
    f = tmp_path / "sample_latin1.csv"
    f.write_bytes("name,city\nAlice,S\xe3o Paulo\nBob,M\xfcnchen\n")
    return str(f)


def test_detect_encoding_utf8(utf8_csv):
    result = detect_encoding(utf8_csv)
    assert "encoding" in result
    assert "confidence" in result
    assert result["encoding"] is not None
    assert result["confidence"] > 0


def test_detect_encoding_returns_fallback_on_empty(tmp_path):
    f = tmp_path / "empty.csv"
    f.write_bytes(b"")
    result = detect_encoding(str(f))
    assert result["encoding"] == FALLBACK_ENCODING


def test_read_with_encoding_auto(utf8_csv):
    content = read_with_encoding(utf8_csv)
    assert "Alice" in content
    assert "São Paulo" in content


def test_read_with_encoding_explicit(latin1_csv):
    content = read_with_encoding(latin1_csv, encoding="latin-1")
    assert "Alice" in content


def test_fix_encoding_produces_utf8(latin1_csv):
    original_enc, fixed = fix_encoding(latin1_csv, target_encoding="utf-8")
    assert isinstance(fixed, str)
    assert "Alice" in fixed
    # Ensure output is valid utf-8
    fixed.encode("utf-8")


def test_fix_encoding_returns_original_encoding(latin1_csv):
    original_enc, _ = fix_encoding(latin1_csv)
    assert isinstance(original_enc, str)
    assert len(original_enc) > 0


def test_write_fixed_file(tmp_path):
    out = tmp_path / "out.csv"
    content = "name,city\nAlice,São Paulo\n"
    write_fixed_file(str(out), content, encoding="utf-8")
    assert out.exists()
    assert out.read_text(encoding="utf-8") == content
