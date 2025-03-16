from rich.box import (
    HEAVY,
    HEAVY_EDGE,
    HEAVY_HEAD,
    MINIMAL,
    MINIMAL_DOUBLE_HEAD,
    MINIMAL_HEAVY_HEAD,
    PLAIN_HEADED_SUBSTITUTIONS,
    SQUARE_DOUBLE_HEAD,
    Box,
)
from rich.console import ConsoleOptions
from rich._loop import loop_last

import pytest


def test_substitute():
    console_options = ConsoleOptions(
        min_width=1,
        max_width=80,
        is_terminal=False,
        encoding="utf-8",
        legacy_windows=False,
        min_height=1,
        max_height=25,
        height=None,
    )

    assert HEAVY_EDGE.substitute(console_options) == HEAVY_EDGE
    assert HEAVY.substitute(console_options) == HEAVY


def test_substitute_legacy_windows():
    console_options = ConsoleOptions(
        min_width=1,
        max_width=80,
        is_terminal=False,
        encoding="utf-8",
        legacy_windows=True,
        min_height=1,
        max_height=25,
        height=None,
    )

    assert HEAVY_EDGE.substitute(console_options) == HEAVY_EDGE
    assert HEAVY.substitute(console_options) == HEAVY


def test_substitute_ascii_only():
    console_options = ConsoleOptions(
        min_width=1,
        max_width=80,
        is_terminal=False,
        encoding="utf-8",
        legacy_windows=False,
        min_height=1,
        max_height=25,
        height=None,
        ascii_only=True,
    )

    assert HEAVY_EDGE.substitute(console_options) == HEAVY_EDGE
    assert HEAVY.substitute(console_options) == HEAVY


@pytest.mark.parametrize(
    "box, expected_box",
    [
        (HEAVY_HEAD, MINIMAL),
        (SQUARE_DOUBLE_HEAD, MINIMAL),
        (MINIMAL_DOUBLE_HEAD, MINIMAL),
        (MINIMAL_HEAVY_HEAD, MINIMAL),
    ],
)
def test_get_plain_headed_box(box: Box, expected_box: Box):
    assert box.get_plain_headed_box() == expected_box


def test_get_top():
    box = HEAVY
    widths = [5, 3, 2]
    expected_top = "┏━━━━━┳━━━┳━━┓"
    assert box.get_top(widths) == expected_top


def test_get_row():
    box = HEAVY
    widths = [5, 3, 2]
    expected_row = "┃     ┃   ┃  ┃"
    assert box.get_row(widths, "row") == expected_row


def test_get_bottom():
    box = HEAVY
    widths = [5, 3, 2]
    expected_bottom = "┗━━━━━┻━━━┻━━┛"
    assert box.get_bottom(widths) == expected_bottom


def test_loop_last():
    assert list(loop_last([1, 2, 3])) == [
        (False, 1),
        (False, 2),
        (True, 3),
    ]

    assert list(loop_last([])) == []