import pytest
from rich.measure import Measurement
from rich.console import Console, ConsoleOptions
from rich.errors import NotRenderableError


@pytest.fixture
def console():
    return Console(width=80)


@pytest.fixture
def options(console):
    return console.options


def test_measurement_span():
    measurement = Measurement(10, 20)
    assert measurement.span == 10


def test_measurement_normalize():
    measurement = Measurement(10, 5)
    normalized = measurement.normalize()
    assert normalized.minimum == 5
    assert normalized.maximum == 5

    measurement = Measurement(-5, 10)
    normalized = measurement.normalize()
    assert normalized.minimum == 0
    assert normalized.maximum == 10


def test_measurement_with_maximum():
    measurement = Measurement(5, 20)
    new_measurement = measurement.with_maximum(10)
    assert new_measurement.minimum == 5
    assert new_measurement.maximum == 10


def test_measurement_with_minimum():
    measurement = Measurement(5, 20)
    new_measurement = measurement.with_minimum(10)
    assert new_measurement.minimum == 10
    assert new_measurement.maximum == 20


def test_measurement_clamp():
    measurement = Measurement(5, 20)
    clamped_measurement = measurement.clamp(min_width=10, max_width=15)
    assert clamped_measurement.minimum == 10
    assert clamped_measurement.maximum == 15


def test_measurement_get_str(console, options):
    measurement = Measurement.get(console, options, "Hello, World!")
    assert measurement.minimum >= 0
    assert measurement.maximum <= options.max_width


def test_measurement_get_non_renderable(console, options):
    class NonRenderable:
        pass

    with pytest.raises(NotRenderableError):
        Measurement.get(console, options, NonRenderable())


def test_measure_renderables(console, options):
    renderables = ["Hello", "World!"]
    measurement = Measurement.get(console, options, renderables)
    assert measurement.minimum >= 0
    assert measurement.maximum <= options.max_width