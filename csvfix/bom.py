"""Detect and strip Byte Order Marks (BOM) from CSV file content."""

BOM_UTF8 = b"\xef\xbb\xbf"
BOM_UTF16_LE = b"\xff\xfe"
BOM_UTF16_BE = b"\xfe\xff"
BOM_UTF32_LE = b"\xff\xfe\x00\x00"
BOM_UTF32_BE = b"\x00\x00\xfe\xff"

KNOWN_BOMS = [
    (BOM_UTF32_LE, "utf-32-le"),
    (BOM_UTF32_BE, "utf-32-be"),
    (BOM_UTF16_LE, "utf-16-le"),
    (BOM_UTF16_BE, "utf-16-be"),
    (BOM_UTF8, "utf-8-sig"),
]


def detect_bom(raw_bytes: bytes) -> tuple[bytes | None, str | None]:
    """Return (bom_bytes, encoding_hint) if a BOM is found, else (None, None)."""
    for bom, encoding in KNOWN_BOMS:
        if raw_bytes.startswith(bom):
            return bom, encoding
    return None, None


def strip_bom(raw_bytes: bytes) -> tuple[bytes, str | None]:
    """Strip BOM from raw bytes if present. Returns (stripped_bytes, encoding_hint)."""
    bom, encoding = detect_bom(raw_bytes)
    if bom:
        return raw_bytes[len(bom):], encoding
    return raw_bytes, None


def has_bom(raw_bytes: bytes) -> bool:
    """Return True if the bytes start with any known BOM."""
    bom, _ = detect_bom(raw_bytes)
    return bom is not None


def strip_bom_from_string(text: str) -> str:
    """Strip the Unicode BOM character from the start of a decoded string."""
    if text.startswith("\ufeff"):
        return text[1:]
    return text


def find_bom_issues(raw_bytes: bytes) -> list[dict]:
    """Return a list of issues if a BOM is detected."""
    bom, encoding = detect_bom(raw_bytes)
    if bom:
        return [{
            "type": "bom_detected",
            "encoding_hint": encoding,
            "bom_hex": bom.hex(),
            "message": f"File starts with a BOM ({encoding}), which may cause parsing issues",
            "severity": "warning",
        }]
    return []
