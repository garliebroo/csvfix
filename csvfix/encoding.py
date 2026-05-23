"""Detect and fix encoding issues in CSV files."""

import chardet


SUPPORTED_ENCODINGS = ["utf-8", "utf-8-sig", "latin-1", "cp1252", "iso-8859-1"]
FALLBACK_ENCODING = "utf-8"


def detect_encoding(file_path: str) -> dict:
    """Detect the encoding of a file using chardet.

    Returns a dict with 'encoding' and 'confidence' keys.
    """
    with open(file_path, "rb") as f:
        raw = f.read()
    result = chardet.detect(raw)
    return {
        "encoding": result.get("encoding") or FALLBACK_ENCODING,
        "confidence": result.get("confidence", 0.0),
    }


def read_with_encoding(file_path: str, encoding: str | None = None) -> str:
    """Read a file, auto-detecting encoding if not provided."""
    if encoding is None:
        encoding = detect_encoding(file_path)["encoding"]
    with open(file_path, "r", encoding=encoding, errors="replace") as f:
        return f.read()


def fix_encoding(file_path: str, target_encoding: str = "utf-8") -> tuple[str, str]:
    """Re-encode a file to the target encoding.

    Returns a tuple of (original_encoding, fixed_content).
    """
    detected = detect_encoding(file_path)
    original_encoding = detected["encoding"]

    with open(file_path, "rb") as f:
        raw = f.read()

    try:
        text = raw.decode(original_encoding, errors="replace")
    except (LookupError, UnicodeDecodeError):
        text = raw.decode(FALLBACK_ENCODING, errors="replace")
        original_encoding = FALLBACK_ENCODING

    fixed_content = text.encode(target_encoding, errors="replace").decode(target_encoding)
    return original_encoding, fixed_content


def write_fixed_file(file_path: str, content: str, encoding: str = "utf-8") -> None:
    """Write fixed content back to a file."""
    with open(file_path, "w", encoding=encoding, newline="") as f:
        f.write(content)


def is_encoding_supported(encoding: str) -> bool:
    """Check whether an encoding is in the supported encodings list.

    Comparison is case-insensitive.
    """
    return encoding.lower() in SUPPORTED_ENCODINGS
