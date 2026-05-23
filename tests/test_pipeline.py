import os
import tempfile
import pytest
from csvfix.pipeline import RepairOptions, RepairReport, total_fixes, repair_file


def write_temp(content: bytes, suffix=".csv"):
    f = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    f.write(content)
    f.close()
    return f.name


def test_total_fixes_zero():
    report = RepairReport()
    assert total_fixes(report) == 0


def test_total_fixes_counts_bom():
    report = RepairReport(bom_removed=True)
    assert total_fixes(report) == 1


def test_total_fixes_sums_all():
    report = RepairReport(
        encoding_fixes=1,
        bom_removed=True,
        line_ending_fixes=2,
        whitespace_fixes=3,
        quote_fixes=1,
        null_fixes=2,
        header_fixes=1,
    )
    assert total_fixes(report) == 11


def test_repair_file_basic(tmp_path):
    csv_content = b"Name,Age,City\nAlice,30,NYC\nBob,25,LA\n"
    input_file = str(tmp_path / "input.csv")
    output_file = str(tmp_path / "output.csv")
    with open(input_file, "wb") as f:
        f.write(csv_content)

    options = RepairOptions(fix_duplicates=False, fix_delimiter=False)
    report = repair_file(input_file, output_file, options)

    assert os.path.exists(output_file)
    assert isinstance(report, RepairReport)


def test_repair_file_strips_bom(tmp_path):
    csv_content = b"\xef\xbb\xbfname,age\nAlice,30\n"
    input_file = str(tmp_path / "input.csv")
    output_file = str(tmp_path / "output.csv")
    with open(input_file, "wb") as f:
        f.write(csv_content)

    options = RepairOptions(fix_bom=True)
    report = repair_file(input_file, output_file, options)
    assert report.bom_removed is True

    result = open(output_file, "rb").read()
    assert not result.startswith(b"\xef\xbb\xbf")


def test_repair_file_no_bom_flag(tmp_path):
    csv_content = b"\xef\xbb\xbfname,age\nAlice,30\n"
    input_file = str(tmp_path / "input.csv")
    output_file = str(tmp_path / "output.csv")
    with open(input_file, "wb") as f:
        f.write(csv_content)

    options = RepairOptions(fix_bom=False)
    report = repair_file(input_file, output_file, options)
    assert report.bom_removed is False


def test_repair_file_default_options(tmp_path):
    csv_content = b"First Name,Last Name\nAlice,Smith\n"
    input_file = str(tmp_path / "input.csv")
    output_file = str(tmp_path / "output.csv")
    with open(input_file, "wb") as f:
        f.write(csv_content)

    report = repair_file(input_file, output_file)
    assert os.path.exists(output_file)
    result = open(output_file).read()
    assert "first_name" in result
