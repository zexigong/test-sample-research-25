from __future__ import annotations

import random
from functools import lru_cache
from typing import Callable

import pytest

from rich.cells import (
    cached_cell_len,
    cell_len,
    chop_cells,
    get_character_cell_size,
    set_cell_size,
)

# Some simple constants to be used in tests
WCWIDTH_2_STR = "🤦🏽‍♂️"
WCWIDTH_2_STR_LEN = len(WCWIDTH_2_STR)
WCWIDTH_2_STR_CELL_LENGTH = 5


@lru_cache
def get_ascii_all() -> str:
    """Get all ASCII characters."""
    return "".join(chr(n) for n in range(32, 127))


ASCII_ALL = get_ascii_all()

# Get a list of all the characters with a single cell width
# The list is taken from the source of rich.cells
_SINGLE_CELL_UNICODE_RANGES: list[tuple[int, int]] = [
    (0x20, 0x7E),  # Latin (excluding non-printable)
    (0xA0, 0xAC),
    (0xAE, 0x002FF),
    (0x00370, 0x00482),  # Greek / Cyrillic
    (0x02500, 0x025FC),  # Box drawing, box elements, geometric shapes
    (0x02800, 0x028FF),  # Braille
]

_SINGLE_CELL_UNICODE_CHARS: list[str] = [
    character
    for _start, _end in _SINGLE_CELL_UNICODE_RANGES
    for character in map(chr, range(_start, _end + 1))
]


def get_random_single_cell_chars(n: int, seed: int = 0) -> str:
    random.seed(seed)
    return "".join(random.choices(_SINGLE_CELL_UNICODE_CHARS, k=n))


def test_get_character_cell_size() -> None:
    """Test the size of a character in cells."""
    _get_character_cell_size = get_character_cell_size
    wcwidth_2_str = WCWIDTH_2_STR
    assert sum(map(_get_character_cell_size, wcwidth_2_str)) == WCWIDTH_2_STR_CELL_LENGTH
    assert sum(map(_get_character_cell_size, wcwidth_2_str)) == WCWIDTH_2_STR_CELL_LENGTH
    assert _get_character_cell_size("a") == 1


@pytest.mark.parametrize(
    "text,expected",
    [
        ("", 0),
        ("abc", 3),
        (WCWIDTH_2_STR, WCWIDTH_2_STR_CELL_LENGTH),
        (get_random_single_cell_chars(512), 512),
        (get_random_single_cell_chars(511) + WCWIDTH_2_STR, 511 + WCWIDTH_2_STR_CELL_LENGTH),
        (get_random_single_cell_chars(513), 513),
        (get_random_single_cell_chars(512) + WCWIDTH_2_STR, 512 + WCWIDTH_2_STR_CELL_LENGTH),
    ],
)
def test_cell_len(text: str, expected: int) -> None:
    """Test the cell length of a string."""
    assert cell_len(text) == expected


@pytest.mark.parametrize(
    "text,expected",
    [
        ("", 0),
        ("abc", 3),
        (WCWIDTH_2_STR, WCWIDTH_2_STR_CELL_LENGTH),
        (get_random_single_cell_chars(512), 512),
        (get_random_single_cell_chars(511) + WCWIDTH_2_STR, 511 + WCWIDTH_2_STR_CELL_LENGTH),
        (get_random_single_cell_chars(513), 513),
        (get_random_single_cell_chars(512) + WCWIDTH_2_STR, 512 + WCWIDTH_2_STR_CELL_LENGTH),
    ],
)
def test_cached_cell_len(text: str, expected: int) -> None:
    """Test the cell length of a string with caching."""
    assert cached_cell_len(text) == expected


@pytest.mark.parametrize(
    "text,expected",
    [
        ("", 0),
        ("abc", 3),
        (WCWIDTH_2_STR, WCWIDTH_2_STR_CELL_LENGTH),
        (get_random_single_cell_chars(512), 512),
        (get_random_single_cell_chars(511) + WCWIDTH_2_STR, 511 + WCWIDTH_2_STR_CELL_LENGTH),
        (get_random_single_cell_chars(513), 513),
        (get_random_single_cell_chars(512) + WCWIDTH_2_STR, 512 + WCWIDTH_2_STR_CELL_LENGTH),
    ],
)
def test_cached_cell_len_vs_cell_len(text: str, expected: int) -> None:
    """Test the cell length of a string with caching."""
    assert cached_cell_len(text) == cell_len(text)


@pytest.mark.parametrize(
    "text,width,expected",
    [
        ("", 1, [""]),
        ("abc", 1, ["a", "b", "c"]),
        ("abc", 2, ["ab", "c"]),
        ("abc", 3, ["abc"]),
        ("abc", 4, ["abc"]),
        ("abc def", 3, ["abc", "def"]),
        ("abc def", 4, ["abc", "def"]),
        ("abc def", 5, ["abc", "def"]),
        ("abc def", 6, ["abc", "def"]),
        ("abc def", 7, ["abc def"]),
        ("abc def", 8, ["abc def"]),
        (WCWIDTH_2_STR, WCWIDTH_2_STR_CELL_LENGTH, [WCWIDTH_2_STR]),
        (WCWIDTH_2_STR, WCWIDTH_2_STR_CELL_LENGTH - 1, [WCWIDTH_2_STR]),
        (WCWIDTH_2_STR, 1, ["🤦🏽‍", "♂️"]),
        (WCWIDTH_2_STR, 2, ["🤦🏽‍", "♂️"]),
        (WCWIDTH_2_STR, 3, ["🤦🏽‍♂️"]),
        (WCWIDTH_2_STR + "a", WCWIDTH_2_STR_CELL_LENGTH, [WCWIDTH_2_STR, "a"]),
        (WCWIDTH_2_STR + "a", WCWIDTH_2_STR_CELL_LENGTH + 1, [WCWIDTH_2_STR + "a"]),
        (WCWIDTH_2_STR + "a", WCWIDTH_2_STR_CELL_LENGTH - 1, [WCWIDTH_2_STR, "a"]),
        (WCWIDTH_2_STR + "aa", WCWIDTH_2_STR_CELL_LENGTH, [WCWIDTH_2_STR, "aa"]),
        (WCWIDTH_2_STR + "aa", WCWIDTH_2_STR_CELL_LENGTH + 1, [WCWIDTH_2_STR + "a", "a"]),
        (WCWIDTH_2_STR + "aa", WCWIDTH_2_STR_CELL_LENGTH + 2, [WCWIDTH_2_STR + "aa"]),
        (WCWIDTH_2_STR + "aa", WCWIDTH_2_STR_CELL_LENGTH - 1, [WCWIDTH_2_STR, "aa"]),
        (WCWIDTH_2_STR + "a" + WCWIDTH_2_STR, WCWIDTH_2_STR_CELL_LENGTH, [WCWIDTH_2_STR, "a", WCWIDTH_2_STR]),
        (
            WCWIDTH_2_STR + "a" + WCWIDTH_2_STR,
            WCWIDTH_2_STR_CELL_LENGTH + 1,
            [WCWIDTH_2_STR + "a", WCWIDTH_2_STR],
        ),
        (
            WCWIDTH_2_STR + "a" + WCWIDTH_2_STR,
            WCWIDTH_2_STR_CELL_LENGTH + 2,
            [WCWIDTH_2_STR + "a", WCWIDTH_2_STR],
        ),
        (
            WCWIDTH_2_STR + "a" + WCWIDTH_2_STR,
            WCWIDTH_2_STR_CELL_LENGTH + 3,
            [WCWIDTH_2_STR + "a" + WCWIDTH_2_STR],
        ),
        (
            WCWIDTH_2_STR + "a" + WCWIDTH_2_STR + "a",
            WCWIDTH_2_STR_CELL_LENGTH,
            [WCWIDTH_2_STR, "a", WCWIDTH_2_STR, "a"],
        ),
        (
            WCWIDTH_2_STR + "a" + WCWIDTH_2_STR + "a",
            WCWIDTH_2_STR_CELL_LENGTH + 1,
            [WCWIDTH_2_STR + "a", WCWIDTH_2_STR, "a"],
        ),
        (
            WCWIDTH_2_STR + "a" + WCWIDTH_2_STR + "a",
            WCWIDTH_2_STR_CELL_LENGTH + 2,
            [WCWIDTH_2_STR + "a", WCWIDTH_2_STR + "a"],
        ),
        (
            WCWIDTH_2_STR + "a" + WCWIDTH_2_STR + "a",
            WCWIDTH_2_STR_CELL_LENGTH + 3,
            [WCWIDTH_2_STR + "a" + WCWIDTH_2_STR, "a"],
        ),
        (
            WCWIDTH_2_STR + "a" + WCWIDTH_2_STR + "a",
            WCWIDTH_2_STR_CELL_LENGTH + 4,
            [WCWIDTH_2_STR + "a" + WCWIDTH_2_STR + "a"],
        ),
        (
            WCWIDTH_2_STR + WCWIDTH_2_STR + WCWIDTH_2_STR + WCWIDTH_2_STR,
            WCWIDTH_2_STR_CELL_LENGTH,
            [WCWIDTH_2_STR, WCWIDTH_2_STR, WCWIDTH_2_STR, WCWIDTH_2_STR],
        ),
        (
            WCWIDTH_2_STR + WCWIDTH_2_STR + WCWIDTH_2_STR + WCWIDTH_2_STR,
            WCWIDTH_2_STR_CELL_LENGTH + 1,
            [WCWIDTH_2_STR, WCWIDTH_2_STR, WCWIDTH_2_STR, WCWIDTH_2_STR],
        ),
        (
            WCWIDTH_2_STR + WCWIDTH_2_STR + WCWIDTH_2_STR + WCWIDTH_2_STR,
            WCWIDTH_2_STR_CELL_LENGTH + 2,
            [WCWIDTH_2_STR + WCWIDTH_2_STR, WCWIDTH_2_STR + WCWIDTH_2_STR],
        ),
        (
            WCWIDTH_2_STR + WCWIDTH_2_STR + WCWIDTH_2_STR + WCWIDTH_2_STR,
            WCWIDTH_2_STR_CELL_LENGTH + 3,
            [WCWIDTH_2_STR + WCWIDTH_2_STR, WCWIDTH_2_STR + WCWIDTH_2_STR],
        ),
        (
            WCWIDTH_2_STR + WCWIDTH_2_STR + WCWIDTH_2_STR + WCWIDTH_2_STR,
            WCWIDTH_2_STR_CELL_LENGTH + 4,
            [WCWIDTH_2_STR + WCWIDTH_2_STR, WCWIDTH_2_STR + WCWIDTH_2_STR],
        ),
        (
            WCWIDTH_2_STR + WCWIDTH_2_STR + WCWIDTH_2_STR + WCWIDTH_2_STR,
            WCWIDTH_2_STR_CELL_LENGTH + 5,
            [WCWIDTH_2_STR + WCWIDTH_2_STR, WCWIDTH_2_STR + WCWIDTH_2_STR],
        ),
        (
            WCWIDTH_2_STR + WCWIDTH_2_STR + WCWIDTH_2_STR + WCWIDTH_2_STR,
            WCWIDTH_2_STR_CELL_LENGTH + 6,
            [WCWIDTH_2_STR + WCWIDTH_2_STR, WCWIDTH_2_STR + WCWIDTH_2_STR],
        ),
        (
            WCWIDTH_2_STR + WCWIDTH_2_STR + WCWIDTH_2_STR + WCWIDTH_2_STR,
            WCWIDTH_2_STR_CELL_LENGTH + 7,
            [WCWIDTH_2_STR + WCWIDTH_2_STR, WCWIDTH_2_STR + WCWIDTH_2_STR],
        ),
        (
            WCWIDTH_2_STR + WCWIDTH_2_STR + WCWIDTH_2_STR + WCWIDTH_2_STR,
            WCWIDTH_2_STR_CELL_LENGTH + 8,
            [WCWIDTH_2_STR + WCWIDTH_2_STR + WCWIDTH_2_STR, WCWIDTH_2_STR],
        ),
        (
            WCWIDTH_2_STR + WCWIDTH_2_STR + WCWIDTH_2_STR + WCWIDTH_2_STR,
            WCWIDTH_2_STR_CELL_LENGTH + 9,
            [WCWIDTH_2_STR + WCWIDTH_2_STR + WCWIDTH_2_STR, WCWIDTH_2_STR],
        ),
        (
            WCWIDTH_2_STR + WCWIDTH_2_STR + WCWIDTH_2_STR + WCWIDTH_2_STR,
            WCWIDTH_2_STR_CELL_LENGTH + 10,
            [WCWIDTH_2_STR + WCWIDTH_2_STR + WCWIDTH_2_STR, WCWIDTH_2_STR],
        ),
        (
            WCWIDTH_2_STR + WCWIDTH_2_STR + WCWIDTH_2_STR + WCWIDTH_2_STR,
            WCWIDTH_2_STR_CELL_LENGTH + 11,
            [WCWIDTH_2_STR + WCWIDTH_2_STR + WCWIDTH_2_STR, WCWIDTH_2_STR],
        ),
        (
            WCWIDTH_2_STR + WCWIDTH_2_STR + WCWIDTH_2_STR + WCWIDTH_2_STR,
            WCWIDTH_2_STR_CELL_LENGTH + 12,
            [WCWIDTH_2_STR + WCWIDTH_2_STR + WCWIDTH_2_STR, WCWIDTH_2_STR],
        ),
        (
            WCWIDTH_2_STR + WCWIDTH_2_STR + WCWIDTH_2_STR + WCWIDTH_2_STR,
            WCWIDTH_2_STR_CELL_LENGTH + 13,
            [WCWIDTH_2_STR + WCWIDTH_2_STR + WCWIDTH_2_STR, WCWIDTH_2_STR],
        ),
        (
            WCWIDTH_2_STR + WCWIDTH_2_STR + WCWIDTH_2_STR + WCWIDTH_2_STR,
            WCWIDTH_2_STR_CELL_LENGTH + 14,
            [WCWIDTH_2_STR + WCWIDTH_2_STR + WCWIDTH_2_STR, WCWIDTH_2_STR],
        ),
        (
            WCWIDTH_2_STR + WCWIDTH_2_STR + WCWIDTH_2_STR + WCWIDTH_2_STR,
            WCWIDTH_2_STR_CELL_LENGTH + 15,
            [WCWIDTH_2_STR + WCWIDTH_2_STR + WCWIDTH_2_STR + WCWIDTH_2_STR],
        ),
        (
            WCWIDTH_2_STR + WCWIDTH_2_STR + WCWIDTH_2_STR + WCWIDTH_2_STR,
            WCWIDTH_2_STR_CELL_LENGTH + 16,
            [WCWIDTH_2_STR + WCWIDTH_2_STR + WCWIDTH_2_STR + WCWIDTH_2_STR],
        ),
    ],
)
def test_chop_cells(text: str, width: int, expected: list[str]) -> None:
    """Test the chop_cells function."""
    assert chop_cells(text, width) == expected


@pytest.mark.parametrize(
    "text,width,expected",
    [
        ("", 1, " "),
        ("", 2, "  "),
        ("", 3, "   "),
        ("abc", 3, "abc"),
        ("abc", 4, "abc "),
        ("abc", 5, "abc  "),
        ("abc", 2, "ab"),
        ("abc", 1, "a"),
        ("abc", 0, ""),
        ("abc", -1, ""),
        ("abc", -2, ""),
        ("abc def", 3, "abc"),
        ("abc def", 4, "abc "),
        ("abc def", 5, "abc d"),
        ("abc def", 6, "abc de"),
        ("abc def", 7, "abc def"),
        ("abc def", 8, "abc def "),
        ("abc def", 9, "abc def  "),
        ("abc def", 10, "abc def   "),
        ("abc def", 11, "abc def    "),
        ("abc def", 12, "abc def     "),
        (WCWIDTH_2_STR, WCWIDTH_2_STR_CELL_LENGTH, WCWIDTH_2_STR),
        (WCWIDTH_2_STR, WCWIDTH_2_STR_CELL_LENGTH + 1, WCWIDTH_2_STR + " "),
        (WCWIDTH_2_STR, WCWIDTH_2_STR_CELL_LENGTH + 2, WCWIDTH_2_STR + "  "),
        (WCWIDTH_2_STR, WCWIDTH_2_STR_CELL_LENGTH + 3, WCWIDTH_2_STR + "   "),
        (WCWIDTH_2_STR, WCWIDTH_2_STR_CELL_LENGTH - 1, "🤦🏽 "),
        (WCWIDTH_2_STR, WCWIDTH_2_STR_CELL_LENGTH - 2, "🤦 "),
        (WCWIDTH_2_STR, WCWIDTH_2_STR_CELL_LENGTH - 3, "🤦 "),
        (WCWIDTH_2_STR, WCWIDTH_2_STR_CELL_LENGTH - 4, "🤦 "),
        (WCWIDTH_2_STR, WCWIDTH_2_STR_CELL_LENGTH - 5, ""),
        (WCWIDTH_2_STR, 1, "🤦🏽 "),
        (WCWIDTH_2_STR, 2, "🤦🏽 "),
        (WCWIDTH_2_STR, 3, "🤦🏽 "),
        (WCWIDTH_2_STR, 4, "🤦🏽 "),
        (WCWIDTH_2_STR, 5, WCWIDTH_2_STR),
        (WCWIDTH_2_STR, 6, WCWIDTH_2_STR + " "),
        (WCWIDTH_2_STR + WCWIDTH_2_STR, WCWIDTH_2_STR_CELL_LENGTH, WCWIDTH_2_STR),
        (WCWIDTH_2_STR + WCWIDTH_2_STR, WCWIDTH_2_STR_CELL_LENGTH + 1, WCWIDTH_2_STR),
        (WCWIDTH_2_STR + WCWIDTH_2_STR, WCWIDTH_2_STR_CELL_LENGTH + 2, WCWIDTH_2_STR + " "),
        (WCWIDTH_2_STR + WCWIDTH_2_STR, WCWIDTH_2_STR_CELL_LENGTH + 3, WCWIDTH_2_STR + " "),
        (WCWIDTH_2_STR + WCWIDTH_2_STR, WCWIDTH_2_STR_CELL_LENGTH + 4, WCWIDTH_2_STR + " "),
        (WCWIDTH_2_STR + WCWIDTH_2_STR, WCWIDTH_2_STR_CELL_LENGTH + 5, WCWIDTH_2_STR + WCWIDTH_2_STR),
        (WCWIDTH_2_STR + WCWIDTH_2_STR, WCWIDTH_2_STR_CELL_LENGTH + 6, WCWIDTH_2_STR + WCWIDTH_2_STR + " "),
        (WCWIDTH_2_STR + WCWIDTH_2_STR, WCWIDTH_2_STR_CELL_LENGTH + 7, WCWIDTH_2_STR + WCWIDTH_2_STR + "  "),
        (WCWIDTH_2_STR + WCWIDTH_2_STR, WCWIDTH_2_STR_CELL_LENGTH + 8, WCWIDTH_2_STR + WCWIDTH_2_STR + "   "),
        (WCWIDTH_2_STR + WCWIDTH_2_STR, WCWIDTH_2_STR_CELL_LENGTH + 9, WCWIDTH_2_STR + WCWIDTH_2_STR + "    "),
        (WCWIDTH_2_STR + WCWIDTH_2_STR, WCWIDTH_2_STR_CELL_LENGTH + 10, WCWIDTH_2_STR + WCWIDTH_2_STR + "     "),
        (WCWIDTH_2_STR + WCWIDTH_2_STR, WCWIDTH_2_STR_CELL_LENGTH - 1, "🤦🏽 "),
        (WCWIDTH_2_STR + WCWIDTH_2_STR, WCWIDTH_2_STR_CELL_LENGTH - 2, "🤦 "),
        (WCWIDTH_2_STR + WCWIDTH_2_STR, WCWIDTH_2_STR_CELL_LENGTH - 3, "🤦 "),
        (WCWIDTH_2_STR + WCWIDTH_2_STR, WCWIDTH_2_STR_CELL_LENGTH - 4, "🤦 "),
        (WCWIDTH_2_STR + WCWIDTH_2_STR, WCWIDTH_2_STR_CELL_LENGTH - 5, ""),
        (WCWIDTH_2_STR + WCWIDTH_2_STR, 1, "🤦🏽 "),
        (WCWIDTH_2_STR + WCWIDTH_2_STR, 2, "🤦🏽 "),
        (WCWIDTH_2_STR + WCWIDTH_2_STR, 3, "🤦🏽 "),
        (WCWIDTH_2_STR + WCWIDTH_2_STR, 4, "🤦🏽 "),
        (WCWIDTH_2_STR + WCWIDTH_2_STR, 5, WCWIDTH_2_STR),
        (WCWIDTH_2_STR + WCWIDTH_2_STR, 6, WCWIDTH_2_STR + " "),
        (WCWIDTH_2_STR + WCWIDTH_2_STR, 7, WCWIDTH_2_STR + " "),
        (WCWIDTH_2_STR + WCWIDTH_2_STR, 8, WCWIDTH_2_STR + " "),
        (WCWIDTH_2_STR + WCWIDTH_2_STR, 9, WCWIDTH_2_STR + WCWIDTH_2_STR),
        (WCWIDTH_2_STR + WCWIDTH_2_STR, 10, WCWIDTH_2_STR + WCWIDTH_2_STR + " "),
        (WCWIDTH_2_STR + WCWIDTH_2_STR, 11, WCWIDTH_2_STR + WCWIDTH_2_STR + "  "),
        (WCWIDTH_2_STR + WCWIDTH_2_STR, 12, WCWIDTH_2_STR + WCWIDTH_2_STR + "   "),
        (WCWIDTH_2_STR + WCWIDTH_2_STR, 13, WCWIDTH_2_STR + WCWIDTH_2_STR + "    "),
        (WCWIDTH_2_STR + WCWIDTH_2_STR, 14, WCWIDTH_2_STR + WCWIDTH_2_STR + "     "),
        (WCWIDTH_2_STR + WCWIDTH_2_STR, 15, WCWIDTH_2_STR + WCWIDTH_2_STR + "      "),
        (WCWIDTH_2_STR + WCWIDTH_2_STR, 16, WCWIDTH_2_STR + WCWIDTH_2_STR + "       "),
        (WCWIDTH_2_STR + WCWIDTH_2_STR, 17, WCWIDTH_2_STR + WCWIDTH_2_STR + "        "),
        (WCWIDTH_2_STR + WCWIDTH_2_STR, 18, WCWIDTH_2_STR + WCWIDTH_2_STR + "         "),
        (WCWIDTH_2_STR + WCWIDTH_2_STR, 19, WCWIDTH_2_STR + WCWIDTH_2_STR + "          "),
        (WCWIDTH_2_STR + WCWIDTH_2_STR, 20, WCWIDTH_2_STR + WCWIDTH_2_STR + "           "),
    ],
)
def test_set_cell_size(text: str, width: int, expected: str) -> None:
    """Test the set_cell_size function."""
    assert set_cell_size(text, width) == expected


@pytest.mark.parametrize(
    "text,width,expected",
    [
        ("", 1, " "),
        ("", 2, "  "),
        ("", 3, "   "),
        ("abc", 3, "abc"),
        ("abc", 4, "abc "),
        ("abc", 5, "abc  "),
        ("abc", 2, "ab"),
        ("abc", 1, "a"),
        ("abc", 0, ""),
        ("abc", -1, ""),
        ("abc", -2, ""),
        ("abc def", 3, "abc"),
        ("abc def", 4, "abc "),
        ("abc def", 5, "abc d"),
        ("abc def", 6, "abc de"),
        ("abc def", 7, "abc def"),
        ("abc def", 8, "abc def "),
        ("abc def", 9, "abc def  "),
        ("abc def", 10, "abc def   "),
        ("abc def", 11, "abc def    "),
        ("abc def", 12, "abc def     "),
        (WCWIDTH_2_STR, WCWIDTH_2_STR_CELL_LENGTH, WCWIDTH_2_STR),
        (WCWIDTH_2_STR, WCWIDTH_2_STR_CELL_LENGTH + 1, WCWIDTH_2_STR + " "),
        (WCWIDTH_2_STR, WCWIDTH_2_STR_CELL_LENGTH + 2, WCWIDTH_2_STR + "  "),
        (WCWIDTH_2_STR, WCWIDTH_2_STR_CELL_LENGTH + 3, WCWIDTH_2_STR + "   "),
        (WCWIDTH_2_STR, WCWIDTH_2_STR_CELL_LENGTH - 1, "🤦🏽 "),
        (WCWIDTH_2_STR, WCWIDTH_2_STR_CELL_LENGTH - 2, "🤦 "),
        (WCWIDTH_2_STR, WCWIDTH_2_STR_CELL_LENGTH - 3, "🤦 "),
        (WCWIDTH_2_STR, WCWIDTH_2_STR_CELL_LENGTH - 4, "🤦 "),
        (WCWIDTH_2_STR, WCWIDTH_2_STR_CELL_LENGTH - 5, ""),
        (WCWIDTH_2_STR, 1, "🤦🏽 "),
        (WCWIDTH_2_STR, 2, "🤦🏽 "),
        (WCWIDTH_2_STR, 3, "🤦🏽 "),
        (WCWIDTH_2_STR, 4, "🤦🏽 "),
        (WCWIDTH_2_STR, 5, WCWIDTH_2_STR),
        (WCWIDTH_2_STR, 6, WCWIDTH_2_STR + " "),
        (WCWIDTH_2_STR + WCWIDTH_2_STR, WCWIDTH_2_STR_CELL_LENGTH, WCWIDTH_2_STR),
        (WCWIDTH_2_STR + WCWIDTH_2_STR, WCWIDTH_2_STR_CELL_LENGTH + 1, WCWIDTH_2_STR),
        (WCWIDTH_2_STR + WCWIDTH_2_STR, WCWIDTH_2_STR_CELL_LENGTH + 2, WCWIDTH_2_STR + " "),
        (WCWIDTH_2_STR + WCWIDTH_2_STR, WCWIDTH_2_STR_CELL_LENGTH + 3, WCWIDTH_2_STR + " "),
        (WCWIDTH_2_STR + WCWIDTH_2_STR, WCWIDTH_2_STR_CELL_LENGTH + 4, WCWIDTH_2_STR + " "),
        (WCWIDTH_2_STR + WCWIDTH_2_STR, WCWIDTH_2_STR_CELL_LENGTH + 5, WCWIDTH_2_STR + WCWIDTH_2_STR),
        (WCWIDTH_2_STR + WCWIDTH_2_STR, WCWIDTH_2_STR_CELL_LENGTH + 6, WCWIDTH_2_STR + WCWIDTH_2_STR + " "),
        (WCWIDTH_2_STR + WCWIDTH_2_STR, WCWIDTH_2_STR_CELL_LENGTH + 7, WCWIDTH_2_STR + WCWIDTH_2_STR + "  "),
        (WCWIDTH_2_STR + WCWIDTH_2_STR, WCWIDTH_2_STR_CELL_LENGTH + 8, WCWIDTH_2_STR + WCWIDTH_2_STR + "   "),
        (WCWIDTH_2_STR + WCWIDTH_2_STR, WCWIDTH_2_STR_CELL_LENGTH + 9, WCWIDTH_2_STR + WCWIDTH_2_STR + "    "),
        (WCWIDTH_2_STR + WCWIDTH_2_STR, WCWIDTH_2_STR_CELL_LENGTH + 10, WCWIDTH_2_STR + WCWIDTH_2_STR + "     "),
        (WCWIDTH_2_STR + WCWIDTH_2_STR, WCWIDTH_2_STR_CELL_LENGTH - 1, "🤦🏽 "),
        (WCWIDTH_2_STR + WCWIDTH_2_STR, WCWIDTH_2_STR_CELL_LENGTH - 2, "🤦 "),
        (WCWIDTH_2_STR + WCWIDTH_2_STR, WCWIDTH_2_STR_CELL_LENGTH - 3, "🤦 "),
        (WCWIDTH_2_STR + WCWIDTH_2_STR, WCWIDTH_2_STR_CELL_LENGTH - 4, "🤦 "),
        (WCWIDTH_2_STR + WCWIDTH_2_STR, WCWIDTH_2_STR_CELL_LENGTH - 5, ""),
        (WCWIDTH_2_STR + WCWIDTH_2_STR, 1, "🤦🏽 "),
        (WCWIDTH_2_STR + WCWIDTH_2_STR, 2, "🤦🏽 "),
        (WCWIDTH_2_STR + WCWIDTH_2_STR, 3, "🤦🏽 "),
        (WCWIDTH_2_STR + WCWIDTH_2_STR, 4, "🤦🏽 "),
        (WCWIDTH_2_STR + WCWIDTH_2_STR, 5, WCWIDTH_2_STR),
        (WCWIDTH_2_STR + WCWIDTH_2_STR, 6, WCWIDTH_2_STR + " "),
        (WCWIDTH_2_STR + WCWIDTH_2_STR, 7, WCWIDTH_2_STR + " "),
        (WCWIDTH_2_STR + WCWIDTH_2_STR, 8, WCWIDTH_2_STR + " "),
        (WCWIDTH_2_STR + WCWIDTH_2_STR, 9, WCWIDTH_2_STR + WCWIDTH_2_STR),
        (WCWIDTH_2_STR + WCWIDTH_2_STR, 10, WCWIDTH_2_STR + WCWIDTH_2_STR + " "),
        (WCWIDTH_2_STR + WCWIDTH_2_STR, 11, WCWIDTH_2_STR + WCWIDTH_2_STR + "  "),
        (WCWIDTH_2_STR + WCWIDTH_2_STR, 12, WCWIDTH_2_STR + WCWIDTH_2_STR + "   "),
        (WCWIDTH_2_STR + WCWIDTH_2_STR, 13, WCWIDTH_2_STR + WCWIDTH_2_STR + "    "),
        (WCWIDTH_2_STR + WCWIDTH_2_STR, 14, WCWIDTH_2_STR + WCWIDTH_2_STR + "     "),
        (WCWIDTH_2_STR + WCWIDTH_2_STR, 15, WCWIDTH_2_STR + WCWIDTH_2_STR + "      "),
        (WCWIDTH_2_STR + WCWIDTH_2_STR, 16, WCWIDTH_2_STR + WCWIDTH_2_STR + "       "),
        (WCWIDTH_2_STR + WCWIDTH_2_STR, 17, WCWIDTH_2_STR + WCWIDTH_2_STR + "        "),
        (WCWIDTH_2_STR + WCWIDTH_2_STR, 18, WCWIDTH_2_STR + WCWIDTH_2_STR + "         "),
        (WCWIDTH_2_STR + WCWIDTH_2_STR, 19, WCWIDTH_2_STR + WCWIDTH_2_STR + "          "),
        (WCWIDTH_2_STR + WCWIDTH_2_STR, 20, WCWIDTH_2_STR + WCWIDTH_2_STR + "           "),
    ],
)
def test_set_cell_size_vs_chop_cells(text: str, width: int, expected: str) -> None:
    """Test the set_cell_size function vs chop_cells."""
    assert "".join(chop_cells(text, width)) == set_cell_size(text, width)