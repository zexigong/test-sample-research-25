from rich.filesize import decimal


def test_decimal():
    assert decimal(1) == "1 byte"
    assert decimal(999) == "999 bytes"
    assert decimal(1000) == "1.0 kB"
    assert decimal(1000 * 1000) == "1.0 MB"
    assert decimal(1000 * 1000 * 1000) == "1.0 GB"
    assert decimal(1000 * 1000 * 1000 * 1000) == "1.0 TB"
    assert decimal(1000 * 1000 * 1000 * 1000 * 1000) == "1.0 PB"
    assert decimal(1000 * 1000 * 1000 * 1000 * 1000 * 1000) == "1.0 EB"
    assert decimal(1000 * 1000 * 1000 * 1000 * 1000 * 1000 * 1000) == "1.0 ZB"
    assert decimal(1000 * 1000 * 1000 * 1000 * 1000 * 1000 * 1000 * 1000) == "1.0 YB"

    assert decimal(1000 * 1000 * 1000 * 1000 * 1000 * 1000 * 1000 * 1000 + 1) == "1,000.0 YB"