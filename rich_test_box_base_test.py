import pytest
from rich.box import Box, ASCII, SQUARE, SIMPLE, HEAVY_HEAD
from rich.console import ConsoleOptions
from rich.test_box.test_box import LEGACY_WINDOWS_SUBSTITUTIONS, PLAIN_HEADED_SUBSTITUTIONS

def test_box_initialization():
    box = Box(
        "┌─┬┐\n"
        "│ ││\n"
        "├─┼┤\n"
        "│ ││\n"
        "├─┼┤\n"
        "├─┼┤\n"
        "│ ││\n"
        "└─┴┘\n"
    )
    assert box.top_left == "┌"
    assert box.top == "─"
    assert box.top_divider == "┬"
    assert box.top_right == "┐"

def test_box_str():
    box = SQUARE
    assert str(box) == (
        "┌─┬┐\n"
        "│ ││\n"
        "├─┼┤\n"
        "│ ││\n"
        "├─┼┤\n"
        "├─┼┤\n"
        "│ ││\n"
        "└─┴┘\n"
    )

def test_box_substitute_legacy_windows():
    options = ConsoleOptions(
        legacy_windows=True,
        min_width=80,
        max_width=80,
        is_terminal=True,
        encoding="utf-8",
        ascii_only=False,
    )
    substituted_box = HEAVY_HEAD.substitute(options)
    assert substituted_box == SQUARE

def test_box_substitute_ascii_only():
    options = ConsoleOptions(
        legacy_windows=False,
        min_width=80,
        max_width=80,
        is_terminal=True,
        encoding="utf-8",
        ascii_only=True,
    )
    substituted_box = SQUARE.substitute(options)
    assert substituted_box == ASCII

def test_box_get_plain_headed_box():
    plain_headed_box = HEAVY_HEAD.get_plain_headed_box()
    assert plain_headed_box == SQUARE

def test_box_get_top():
    box = SIMPLE
    top = box.get_top([3, 5, 2])
    assert top == "─── ───── ──"

def test_box_get_row():
    box = SIMPLE
    row = box.get_row([3, 5, 2])
    assert row == "─── ───── ──"

def test_box_get_bottom():
    box = SIMPLE
    bottom = box.get_bottom([3, 5, 2])
    assert bottom == "─── ───── ──"

def test_legacy_windows_substitution():
    assert LEGACY_WINDOWS_SUBSTITUTIONS[HEAVY_HEAD] == SQUARE

def test_plain_headed_substitution():
    assert PLAIN_HEADED_SUBSTITUTIONS[HEAVY_HEAD] == SQUARE