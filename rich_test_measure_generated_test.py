# These tests are primarily for the rich.measure module, but require elements of rich.console too.

from typing import List

import pytest

from rich.console import ConsoleOptions
from rich.measure import Measurement, measure_renderables


class Ruler:
    def __init__(self, width: int) -> None:
        self.width = width

    def __rich_measure__(self, console, options):
        return Measurement(self.width, self.width)

    def __rich_console__(self, console, options):
        yield "—" * self.width


def test_measure():
    console = ConsoleOptions(
        size=(80, 25), legacy_windows=False, min_width=0, max_width=80, is_terminal=True
    )
    options = console.update_dimensions(12, 12)
    ruler = Ruler(12)
    measurement = Measurement.get(console, options, ruler)
    assert measurement.minimum == 12
    assert measurement.maximum == 12


def test_measure_renderables():
    console = ConsoleOptions(
        size=(80, 25), legacy_windows=False, min_width=0, max_width=80, is_terminal=True
    )
    options = console.update_dimensions(12, 12)
    ruler = Ruler(12)
    measurement = measure_renderables(console, options, [ruler, "foo", "bar"])
    assert measurement.minimum == 12
    assert measurement.maximum == 12


@pytest.mark.parametrize(
    "minimum, maximum, expected",
    [
        (0, 0, (0, 0)),
        (1, 1, (1, 1)),
        (1, 2, (1, 2)),
        (2, 1, (1, 2)),
        (5, 5, (5, 5)),
        (5, 10, (5, 10)),
        (10, 5, (5, 10)),
        (10, 5, (5, 10)),
    ],
)
def test_normalize(minimum: int, maximum: int, expected: List[int]):
    m = Measurement(minimum, maximum)
    result = m.normalize()
    assert result == Measurement(*expected)


@pytest.mark.parametrize(
    "minimum, maximum, width, expected",
    [
        (0, 0, 0, (0, 0)),
        (1, 1, 1, (1, 1)),
        (1, 2, 1, (1, 1)),
        (2, 1, 2, (1, 1)),
        (5, 5, 5, (5, 5)),
        (5, 10, 5, (5, 5)),
        (10, 5, 10, (5, 10)),
        (10, 5, 10, (5, 10)),
    ],
)
def test_with_maximum(minimum: int, maximum: int, width: int, expected: List[int]):
    m = Measurement(minimum, maximum)
    result = m.with_maximum(width)
    assert result == Measurement(*expected)


@pytest.mark.parametrize(
    "minimum, maximum, width, expected",
    [
        (0, 0, 0, (0, 0)),
        (1, 1, 1, (1, 1)),
        (1, 2, 1, (1, 2)),
        (2, 1, 2, (2, 2)),
        (5, 5, 5, (5, 5)),
        (5, 10, 5, (5, 10)),
        (10, 5, 10, (10, 10)),
        (10, 5, 10, (10, 10)),
    ],
)
def test_with_minimum(minimum: int, maximum: int, width: int, expected: List[int]):
    m = Measurement(minimum, maximum)
    result = m.with_minimum(width)
    assert result == Measurement(*expected)


@pytest.mark.parametrize(
    "minimum, maximum, min_width, max_width, expected",
    [
        (0, 0, 0, None, (0, 0)),
        (1, 1, 1, None, (1, 1)),
        (1, 2, 1, None, (1, 2)),
        (2, 1, 2, None, (2, 2)),
        (5, 5, 5, None, (5, 5)),
        (5, 10, 5, None, (5, 10)),
        (10, 5, 10, None, (10, 10)),
        (10, 5, 10, None, (10, 10)),
        (0, 0, None, 0, (0, 0)),
        (1, 1, None, 1, (1, 1)),
        (1, 2, None, 1, (1, 1)),
        (2, 1, None, 2, (1, 1)),
        (5, 5, None, 5, (5, 5)),
        (5, 10, None, 5, (5, 5)),
        (10, 5, None, 10, (5, 10)),
        (10, 5, None, 10, (5, 10)),
        (0, 0, 0, 0, (0, 0)),
        (1, 1, 1, 1, (1, 1)),
        (1, 2, 1, 1, (1, 1)),
        (2, 1, 2, 2, (2, 2)),
        (5, 5, 5, 5, (5, 5)),
        (5, 10, 5, 5, (5, 5)),
        (10, 5, 10, 10, (10, 10)),
        (10, 5, 10, 10, (10, 10)),
    ],
)
def test_clamp(
    minimum: int, maximum: int, min_width: int, max_width: int, expected: List[int]
):
    m = Measurement(minimum, maximum)
    result = m.clamp(min_width, max_width)
    assert result == Measurement(*expected)