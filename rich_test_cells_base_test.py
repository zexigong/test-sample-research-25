import pytest
from rich._cell_widths import CELL_WIDTHS
from rich.test_cells import (
    cached_cell_len,
    cell_len,
    get_character_cell_size,
    set_cell_size,
    chop_cells,
)

@pytest.mark.parametrize("text, expected", [
    ("", 0),
    ("abc", 3),
    ("这是对亚洲语言支持的测试。", 28),
    ("😽", 2),
])
def test_cached_cell_len(text, expected):
    assert cached_cell_len(text) == expected

@pytest.mark.parametrize("text, expected", [
    ("", 0),
    ("abc", 3),
    ("这是对亚洲语言支持的测试。", 28),
    ("😽", 2),
])
def test_cell_len(text, expected):
    assert cell_len(text) == expected

@pytest.mark.parametrize("character, expected", [
    ("a", 1),
    ("Ω", 1),
    ("😽", 2),
    ("\u200B", 0),  # Zero width space
])
def test_get_character_cell_size(character, expected):
    assert get_character_cell_size(character) == expected

@pytest.mark.parametrize("text, total, expected", [
    ("abc", 5, "abc  "),
    ("这是测试", 8, "这是测试"),
    ("这是测试", 4, "这是测试"),
    ("这是测试", 2, "这是"),
    ("abc", 0, ""),
])
def test_set_cell_size(text, total, expected):
    assert set_cell_size(text, total) == expected

@pytest.mark.parametrize("text, width, expected", [
    ("abc", 1, ["a", "b", "c"]),
    ("这是对亚洲语言支持的测试。", 8, ["这是对", "亚洲语言", "支持的测", "试。"]),
    ("😽😽😽", 4, ["😽😽", "😽"]),
    ("", 5, [""]),
])
def test_chop_cells(text, width, expected):
    assert chop_cells(text, width) == expected