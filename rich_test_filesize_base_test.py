import pytest
from rich.filesize import decimal, _to_str, pick_unit_and_suffix

def test_decimal_basic_usage():
    assert decimal(1) == "1 byte"
    assert decimal(999) == "999 bytes"
    assert decimal(1000) == "1.0 kB"
    assert decimal(1500) == "1.5 kB"
    assert decimal(1000000) == "1.0 MB"
    assert decimal(1234567890) == "1.2 GB"

def test_decimal_precision():
    assert decimal(1500, precision=2) == "1.50 kB"
    assert decimal(1234567890, precision=3) == "1.235 GB"

def test_decimal_separator():
    assert decimal(1500, separator="") == "1.5kB"
    assert decimal(1234567890, separator="-") == "1.2-GB"

def test_to_str():
    suffixes = ("kB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    assert _to_str(1, suffixes, 1000) == "1 byte"
    assert _to_str(999, suffixes, 1000) == "999 bytes"
    assert _to_str(1000, suffixes, 1000) == "1.0 kB"
    assert _to_str(1500, suffixes, 1000) == "1.5 kB"

def test_pick_unit_and_suffix():
    suffixes = ["bytes", "kB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB"]
    assert pick_unit_and_suffix(1, suffixes, 1000) == (1, "bytes")
    assert pick_unit_and_suffix(1500, suffixes, 1000) == (1000, "kB")
    assert pick_unit_and_suffix(1500000, suffixes, 1000) == (1000000, "MB")

@pytest.mark.parametrize(
    "size,expected",
    [
        (1, "1 byte"),
        (999, "999 bytes"),
        (1000, "1.0 kB"),
        (1500, "1.5 kB"),
        (1000000, "1.0 MB"),
        (1234567890, "1.2 GB"),
    ],
)
def test_decimal_various_sizes(size, expected):
    assert decimal(size) == expected

@pytest.mark.parametrize(
    "size,precision,expected",
    [
        (1500, 2, "1.50 kB"),
        (1234567890, 3, "1.235 GB"),
    ],
)
def test_decimal_various_precisions(size, precision, expected):
    assert decimal(size, precision=precision) == expected

@pytest.mark.parametrize(
    "size,separator,expected",
    [
        (1500, "", "1.5kB"),
        (1234567890, "-", "1.2-GB"),
    ],
)
def test_decimal_various_separators(size, separator, expected):
    assert decimal(size, separator=separator) == expected