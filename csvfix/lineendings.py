"""Detect and normalize line ending styles in CSV files."""

import re
from enum import Enum


class LineEnding(str, Enum):
    CRLF = "\r\n"
    LF = "\n"
    CR = "\r"
    MIXED = "mixed"


def detect_line_ending(content: str) -> LineEnding:
    """Detect the dominant line ending style in raw file content."""
    crlf_count = content.count("\r\n")
    # Avoid counting the \r in \r\n as standalone CR
    cr_count = len(re.findall(r"\r(?!\n)", content))
    lf_count = len(re.findall(r"(?<!\r)\n", content))

    counts = {LineEnding.CRLF: crlf_count, LineEnding.LF: lf_count, LineEnding.CR: cr_count}
    nonzero = {k: v for k, v in counts.items() if v > 0}

    if not nonzero:
        return LineEnding.LF  # default fallback

    if len(nonzero) > 1:
        return LineEnding.MIXED

    return max(nonzero, key=lambda k: nonzero[k])


def normalize_line_endings(content: str, target: LineEnding = LineEnding.LF) -> str:
    """Normalize all line endings in content to the target style."""
    if target == LineEnding.MIXED:
        raise ValueError("Cannot normalize to mixed line endings")

    # First, unify everything to \n
    unified = content.replace("\r\n", "\n").replace("\r", "\n")

    if target == LineEnding.LF:
        return unified
    elif target == LineEnding.CRLF:
        return unified.replace("\n", "\r\n")
    elif target == LineEnding.CR:
        return unified.replace("\n", "\r")

    return unified


def find_line_ending_issues(content: str) -> list[dict]:
    """Return a list of issues found with line endings."""
    issues = []
    ending = detect_line_ending(content)

    if ending == LineEnding.MIXED:
        issues.append({
            "type": "mixed_line_endings",
            "message": "File contains mixed line ending styles (CRLF, LF, and/or CR)",
            "severity": "warning",
        })
    elif ending == LineEnding.CR:
        issues.append({
            "type": "cr_line_endings",
            "message": "File uses legacy CR-only line endings",
            "severity": "info",
        })
    elif ending == LineEnding.CRLF:
        issues.append({
            "type": "crlf_line_endings",
            "message": "File uses Windows-style CRLF line endings",
            "severity": "info",
        })

    return issues
