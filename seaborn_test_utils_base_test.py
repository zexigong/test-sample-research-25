import pytest
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import to_rgb
from seaborn.test_utils import (
    ci_to_errsize, desaturate, saturate, set_hls_values,
    remove_na, get_color_cycle, despine, move_legend, load_dataset, 
    axis_ticklabels_overlap, axes_ticklabels_overlap, ci
)


def test_ci_to_errsize():
    cis = [[1, 2], [3, 4]]
    heights = [2, 3]
    expected = np.array([[1, 1], [1, 1]])
    result = ci_to_errsize(cis, heights)
    np.testing.assert_array_equal(result, expected)


def test_desaturate():
    color = "#FF0000"  # Red
    prop = 0.5
    expected = colorsys.hls_to_rgb(*colorsys.rgb_to_hls(*to_rgb(color))[:2], 0.5)
    result = desaturate(color, prop)
    assert result == pytest.approx(expected)


def test_saturate():
    color = "#FFAAAA"  # Light red
    expected = (1.0, 0.0, 0.0)  # Fully saturated red
    result = saturate(color)
    assert result == pytest.approx(expected)


def test_set_hls_values():
    color = "#FFAAAA"
    new_l = 0.5
    expected = colorsys.hls_to_rgb(*colorsys.rgb_to_hls(*to_rgb(color))[:1], new_l, 1.0)
    result = set_hls_values(color, l=new_l)
    assert result == pytest.approx(expected)


def test_remove_na():
    vector = pd.Series([1, 2, np.nan, 4])
    expected = pd.Series([1, 2, 4], index=[0, 1, 3])
    result = remove_na(vector)
    pd.testing.assert_series_equal(result, expected)


def test_get_color_cycle():
    colors = get_color_cycle()
    assert isinstance(colors, list)
    assert all(isinstance(c, str) for c in colors)


def test_despine():
    fig, ax = plt.subplots()
    despine(ax=ax, top=True, right=True)
    assert not ax.spines["top"].get_visible()
    assert not ax.spines["right"].get_visible()
    assert ax.spines["left"].get_visible()
    assert ax.spines["bottom"].get_visible()
    plt.close(fig)


def test_move_legend():
    fig, ax = plt.subplots()
    ax.plot([0, 1], label="test")
    ax.legend(loc="upper right")
    move_legend(ax, loc="lower left")
    legend = ax.get_legend()
    assert legend._loc == 3  # 'lower left' location code
    plt.close(fig)


def test_load_dataset():
    df = load_dataset("tips")
    assert isinstance(df, pd.DataFrame)
    assert not df.empty


def test_axis_ticklabels_overlap():
    fig, ax = plt.subplots()
    ax.set_xticks([0, 1])
    ax.set_xticklabels(["a", "b"])
    assert not axis_ticklabels_overlap(ax.get_xticklabels())
    plt.close(fig)


def test_axes_ticklabels_overlap():
    fig, ax = plt.subplots()
    ax.set_xticks([0, 1])
    ax.set_xticklabels(["a", "b"])
    x_overlap, y_overlap = axes_ticklabels_overlap(ax)
    assert not x_overlap
    assert not y_overlap
    plt.close(fig)


def test_ci():
    data = np.array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    lower, upper = ci(data, which=95)
    assert lower < upper
    assert lower > 0
    assert upper < 10