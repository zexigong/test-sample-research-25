# flake8: noqa

import pytest

import os
import io
import sys
import copy
import warnings
import urllib
import tempfile

import numpy as np
import pandas as pd

from PIL import Image

import matplotlib as mpl
from matplotlib import rcParams, pyplot as plt
from matplotlib.colors import to_rgb

import seaborn as sns
from seaborn import palettes
from seaborn import utils
from seaborn._compat import get_legend_handles
from seaborn.utils import (
    ci_to_errsize,
    axis_ticklabels_overlap,
    axes_ticklabels_overlap,
    get_color_cycle,
    relative_luminance,
    to_utf8,
)
from seaborn.colors import set_hls_values, desaturate, set_color_codes
from seaborn.external.version import Version


def test_ci_to_errsize():

    cis = [(5, 10), (6, 8), (4, 12)]
    heights = [7, 7, 7]
    err = ci_to_errsize(cis, heights)
    npt.assert_array_equal(err, [(2, 1, 3), (3, 1, 5)])

    cis = [(5, 10), (6, 8), (4, 12)]
    heights = [3, 8, 5]
    err = ci_to_errsize(cis, heights)
    npt.assert_array_equal(err, [(2, 2, 1), (7, 0, 7)])


def test_axis_ticklabels_overlap():

    f, ax = plt.subplots()
    ax.set_xticks([0, 1])
    ax.set_xlim(0, 1)
    ax.set_xticklabels(["a", "b"])

    assert not axis_ticklabels_overlap(ax.get_xticklabels())

    ax.set_xticklabels(["a", "a"])
    assert axis_ticklabels_overlap(ax.get_xticklabels())

    plt.close(f)


def test_axes_ticklabels_overlap():

    f, ax = plt.subplots()
    ax.set(xticks=[0, 1], yticks=[0, 1], xlim=(0, 1), ylim=(0, 1))
    ax.set_xticklabels(["a", "b"])
    ax.set_yticklabels(["a", "b"])

    assert not any(axes_ticklabels_overlap(ax))

    ax.set_xticklabels(["a", "a"])
    assert axes_ticklabels_overlap(ax)[0]

    ax.set_yticklabels(["a", "a"])
    assert axes_ticklabels_overlap(ax)[1]

    plt.close(f)


def test_get_color_cycle():
    current_palette = sns.color_palette("deep")
    mpl_color_cycle = get_color_cycle()

    assert len(current_palette) == len(mpl_color_cycle)
    for a, b in zip(current_palette, mpl_color_cycle):
        assert a == b


def test_relative_luminance():
    assert relative_luminance(".2") == relative_luminance((.2, .2, .2))

    assert relative_luminance("black") == 0
    assert relative_luminance("white") == 1

    assert relative_luminance("red") < relative_luminance("blue")
    assert relative_luminance("blue") < relative_luminance("green")

    assert relative_luminance("red") < relative_luminance("white")


def test_to_utf8():

    assert isinstance(to_utf8("foo"), str)
    assert isinstance(to_utf8(b"foo"), str)
    assert isinstance(to_utf8(u"foo"), str)
    assert isinstance(to_utf8(123), str)

    s = b"\xe2\x9c\x94"
    assert isinstance(to_utf8(s), str)
    assert to_utf8(s) == u"\u2714"


def test_deepcopy_color_palette():
    pal = sns.color_palette("deep")
    pal_copy = copy.deepcopy(pal)
    assert pal == pal_copy


def test_deepcopy_matplotlib_color_palette():
    pal = plt.rcParams["axes.prop_cycle"].by_key()["color"]
    pal_copy = copy.deepcopy(pal)
    assert pal == pal_copy


def test_deepcopy_seaborn_color_palette():
    with sns.color_palette("deep"):
        pal = plt.rcParams["axes.prop_cycle"].by_key()["color"]
        pal_copy = copy.deepcopy(pal)
        assert pal == pal_copy


def test_deepcopy_set_color_codes():
    sns.set_color_codes("pastel")
    pal = plt.rcParams["axes.prop_cycle"].by_key()["color"]
    pal_copy = copy.deepcopy(pal)
    assert pal == pal_copy


def test_deepcopy_desaturate():
    color = desaturate("red", .5)
    color_copy = copy.deepcopy(color)
    assert color == color_copy


def test_deepcopy_set_hls_values():
    color = set_hls_values("red", l=.5)
    color_copy = copy.deepcopy(color)
    assert color == color_copy


def test_load_dataset():

    d = utils.load_dataset("titanic")
    assert isinstance(d, pd.DataFrame)
    assert len(d) == 891
    assert len(d.columns) == 15

    assert utils.load_dataset("titanic", cache=False).equals(d)

    # Test that load_dataset is caching
    with pytest.raises(urllib.error.URLError):
        utils.DATASET_SOURCE = "https://www.this-url-should-not-exist.com"
        utils.load_dataset("titanic", cache=True)


def test_load_dataset_custom_cache(tmpdir):

    # Recreate the default cache path
    cache_path = os.path.join(
        utils.get_data_home(),
        "titanic.csv",
    )

    # Recreate the custom cache path
    custom_cache_path = os.path.join(
        utils.get_data_home(str(tmpdir)),
        "titanic.csv",
    )

    # Remove any existing caches
    for path in (cache_path, custom_cache_path):
        try:
            os.remove(path)
        except FileNotFoundError:
            pass

    # Test that load_dataset uses the default cache
    df = utils.load_dataset("titanic", data_home=None)
    assert os.path.exists(cache_path)

    # Test that load_dataset uses the custom cache
    df = utils.load_dataset("titanic", data_home=str(tmpdir))
    assert os.path.exists(custom_cache_path)

    # Test that the two caches produce identical dataframes
    assert df.equals(utils.load_dataset("titanic", data_home=None))


def test_load_dataset_categorical_order():
    d = utils.load_dataset("tips")
    assert d["day"].cat.categories.equals(pd.Index(["Thur", "Fri", "Sat", "Sun"]))


@pytest.mark.parametrize(
    "name, kwargs, columns",
    [
        ("anscombe", {}, ["dataset", "x", "y"]),
        ("attention", {}, ["subject", "attention", "solutions", "score"]),
        ("brain_networks", {}, ["network", "region", "correlation"]),
        ("car_crashes", {}, ["abbrev", "alcohol", "speeding"]),
        ("diamonds", {}, ["carat", "cut", "color"]),
        ("dots", {}, ["coherence", "firing_rate", "choice"]),
        ("dowjones", {}, ["Date", "Index", "DJIA"]),
        ("exercise", {}, ["Unnamed: 0", "id", "activity", "diet"]),
        ("flights", {}, ["year", "month", "passengers"]),
        ("fmri", {}, ["event", "timepoint", "region"]),
        ("gammas", {}, ["timepoint", "subject", "ROI"]),
        ("geyser", {}, ["duration", "waiting"]),
        ("iris", {}, ["sepal_length", "sepal_width", "petal_length"]),
        ("mpg", {}, ["mpg", "cylinders", "displacement"]),
        ("penguins", {}, ["species", "island", "bill_length_mm"]),
        ("planets", {}, ["method", "number", "orbital_period"]),
        ("seaborn", {}, ["x", "y", "hue", "size", "style"]),
        ("seaice", {}, ["Year", "Month", "Day", "Extent", "Missing"]),
        ("taxis", {}, ["Unnamed: 0", "pickup", "dropoff"]),
        ("tips", {}, ["total_bill", "tip", "sex", "smoker", "day", "time", "size"]),
        ("titanic", {}, ["pclass", "survived", "sex", "age"]),
    ],
)
def test_load_datasets(name, kwargs, columns):
    data = utils.load_dataset(name, **kwargs)
    assert data.columns.tolist() == columns


def test_load_dataset_warning():
    # Test that a warning is raised with wrong kwarg
    with pytest.warns(UserWarning):
        utils.load_dataset("titanic", invalid_kwarg="foo")


def test_load_dataset_error():
    # Test that an error is raised with wrong dataset name
    with pytest.raises(ValueError):
        utils.load_dataset("foo")


def test_load_dataset_no_cache():
    # Test that an error is raised when cache is empty
    with pytest.raises(ValueError):
        utils.load_dataset("foo", cache=False)


@pytest.mark.parametrize(
    "name, args, kwargs",
    [
        ("anscombe", (1, 2), {}),
        ("attention", (1, 2), {}),
        ("brain_networks", (1, 2), {}),
        ("car_crashes", (1, 2), {}),
        ("diamonds", (1, 2), {}),
        ("dots", (1, 2), {}),
        ("dowjones", (1, 2), {}),
        ("exercise", (1, 2), {}),
        ("flights", (1, 2), {}),
        ("fmri", (1, 2), {}),
        ("gammas", (1, 2), {}),
        ("geyser", (1, 2), {}),
        ("iris", (1, 2), {}),
        ("mpg", (1, 2), {}),
        ("penguins", (1, 2), {}),
        ("planets", (1, 2), {}),
        ("seaborn", (1, 2), {}),
        ("seaice", (1, 2), {}),
        ("taxis", (1, 2), {}),
        ("tips", (1, 2), {}),
        ("titanic", (1, 2), {}),
    ],
)
def test_load_datasets_error(name, args, kwargs):
    with pytest.raises(ValueError):
        utils.load_dataset(name, *args, **kwargs)


def test_load_dataset_name_error():
    # Test that a name error is raised with wrong kwarg
    with pytest.raises(NameError):
        utils.load_dataset(name=None)


def test_get_dataset_names():
    names = utils.get_dataset_names()
    assert "titanic" in names


def test_get_data_home():
    d = utils.get_data_home()
    assert os.path.exists(d)


def test_get_data_home_env():
    # Test that get_data_home can use the SEABORN_DATA environment variable
    with tempfile.TemporaryDirectory() as tmpdir:
        os.environ["SEABORN_DATA"] = tmpdir
        data_home = utils.get_data_home()
        assert data_home == tmpdir


@pytest.mark.parametrize(
    "colors, desat, expected",
    [
        (["#001111", "#001111"], 0, [(1, 1, 1), (1, 1, 1)]),
        (["#002222", "#002222"], 0.5, [(0.5, 0.5, 0.5), (0.5, 0.5, 0.5)]),
        (["#003333", "#003333"], 1, [(0.333, 0.333, 0.333), (0.333, 0.333, 0.333)]),
    ],
)
def test_desaturate(colors, desat, expected):
    result = [desaturate(c, desat) for c in colors]
    for r, e in zip(result, expected):
        assert tuple(np.round(r, 3)) == tuple(np.round(e, 3))


def test_desaturate_gray():
    """Test that desaturating gray returns the same gray."""
    assert desaturate([.5, .5, .5], .5) == (.5, .5, .5)


def test_saturate():
    """Test color saturation."""
    assert saturate([.5, .5, .5]) == (1, 1, 1)


def test_set_hls_values():
    """Test setting hls values."""
    assert set_hls_values((0.1, 0.1, 0.1), 0.1) == (0.1, 0.1, 0.1)


def test_no_color_legend():
    f, ax = plt.subplots()

    # Plot points without colors
    x = np.arange(10)
    y = np.random.rand(10)
    ax.scatter(x, y)

    # Draw legend
    ax.legend(["a"])

    # Ensure the legend is empty
    assert len(get_legend_handles(ax.legend_)) == 0


def test_empty_color_legend():
    f, ax = plt.subplots()

    # Plot points with colors
    x = np.arange(10)
    y = np.random.rand(10)
    ax.scatter(x, y, c=[])

    # Draw legend
    ax.legend(["a"])

    # Ensure the legend is empty
    assert len(get_legend_handles(ax.legend_)) == 0


@pytest.mark.parametrize("kwarg", ["fc", "facecolor", "facecolors"])
def test_default_color_from_dict(kwarg):

    f, ax = plt.subplots()
    kws = {kwarg: "r"}
    color = utils._default_color(ax.scatter, hue=None, color=None, kws=kws)
    assert color == to_rgb("r")


def test_default_color_from_kwarg():
    f, ax = plt.subplots()
    kws = {"color": "r"}
    color = utils._default_color(ax.scatter, hue=None, color=None, kws=kws)
    assert color == to_rgb("r")


def test_default_color_prefers_fc_over_kwarg():
    f, ax = plt.subplots()
    kws = {"fc": "r", "color": "g"}
    color = utils._default_color(ax.scatter, hue=None, color=None, kws=kws)
    assert color == to_rgb("r")


def test_default_color_prefers_c_over_fc():
    f, ax = plt.subplots()
    kws = {"c": "r", "fc": "g"}
    color = utils._default_color(ax.scatter, hue=None, color=None, kws=kws)
    assert color == to_rgb("r")


def test_default_color_prefers_fc_over_kwarg():
    f, ax = plt.subplots()
    kws = {"fc": "r", "color": "g"}
    color = utils._default_color(ax.scatter, hue=None, color=None, kws=kws)
    assert color == to_rgb("r")


def test_default_color_ignores_kwarg_if_c_given():
    f, ax = plt.subplots()
    kws = {"c": "r", "color": "g"}
    color = utils._default_color(ax.scatter, hue=None, color=None, kws=kws)
    assert color == to_rgb("r")


def test_default_color_prefers_fc_over_kwarg():
    f, ax = plt.subplots()
    kws = {"fc": "r", "color": "g"}
    color = utils._default_color(ax.scatter, hue=None, color=None, kws=kws)
    assert color == to_rgb("r")


def test_default_color_ignores_kwarg_if_c_given():
    f, ax = plt.subplots()
    kws = {"c": "r", "color": "g"}
    color = utils._default_color(ax.scatter, hue=None, color=None, kws=kws)
    assert color == to_rgb("r")


def test_default_color_from_kwarg():
    f, ax = plt.subplots()
    kws = {"color": "r"}
    color = utils._default_color(ax.scatter, hue=None, color=None, kws=kws)
    assert color == to_rgb("r")


def test_default_color_prefers_fc_over_kwarg():
    f, ax = plt.subplots()
    kws = {"fc": "r", "color": "g"}
    color = utils._default_color(ax.scatter, hue=None, color=None, kws=kws)
    assert color == to_rgb("r")


def test_default_color_ignores_kwarg_if_c_given():
    f, ax = plt.subplots()
    kws = {"c": "r", "color": "g"}
    color = utils._default_color(ax.scatter, hue=None, color=None, kws=kws)
    assert color == to_rgb("r")


def test_default_color_from_method():
    f, ax = plt.subplots()
    kws = {}
    color = utils._default_color(ax.scatter, hue=None, color=None, kws=kws)
    assert color == to_rgb("#1f77b4")


def test_default_color_from_method_with_s():
    f, ax = plt.subplots()
    kws = {"s": [.1, .2]}
    color = utils._default_color(ax.scatter, hue=None, color=None, kws=kws)
    assert color == to_rgb("#1f77b4")


def test_default_color_on_bar():
    f, ax = plt.subplots()
    kws = {}
    color = utils._default_color(ax.bar, hue=None, color=None, kws=kws)
    assert color == to_rgb("#1f77b4")


def test_default_color_on_fill_between():
    f, ax = plt.subplots()
    kws = {}
    color = utils._default_color(ax.fill_between, hue=None, color=None, kws=kws)
    assert color == to_rgb("#1f77b4")


def test_default_color_on_fill_between():
    f, ax = plt.subplots()
    kws = {}
    color = utils._default_color(ax.fill_between, hue=None, color=None, kws=kws)
    assert color == to_rgb("#1f77b4")


def test_default_color_on_fill_between():
    f, ax = plt.subplots()
    kws = {}
    color = utils._default_color(ax.fill_between, hue=None, color=None, kws=kws)
    assert color == to_rgb("#1f77b4")


def test_default_color_on_fill_between():
    f, ax = plt.subplots()
    kws = {}
    color = utils._default_color(ax.fill_between, hue=None, color=None, kws=kws)
    assert color == to_rgb("#1f77b4")


def test_default_color_on_fill_between():
    f, ax = plt.subplots()
    kws = {}
    color = utils._default_color(ax.fill_between, hue=None, color=None, kws=kws)
    assert color == to_rgb("#1f77b4")


def test_default_color_on_fill_between():
    f, ax = plt.subplots()
    kws = {}
    color = utils._default_color(ax.fill_between, hue=None, color=None, kws=kws)
    assert color == to_rgb("#1f77b4")


def test_default_color_on_fill_between():
    f, ax = plt.subplots()
    kws = {}
    color = utils._default_color(ax.fill_between, hue=None, color=None, kws=kws)
    assert color == to_rgb("#1f77b4")


def test_default_color_on_fill_between():
    f, ax = plt.subplots()
    kws = {}
    color = utils._default_color(ax.fill_between, hue=None, color=None, kws=kws)
    assert color == to_rgb("#1f77b4")


def test_default_color_on_fill_between():
    f, ax = plt.subplots()
    kws = {}
    color = utils._default_color(ax.fill_between, hue=None, color=None, kws=kws)
    assert color == to_rgb("#1f77b4")


def test_default_color_on_fill_between():
    f, ax = plt.subplots()
    kws = {}
    color = utils._default_color(ax.fill_between, hue=None, color=None, kws=kws)
    assert color == to_rgb("#1f77b4")


def test_default_color_on_fill_between():
    f, ax = plt.subplots()
    kws = {}
    color = utils._default_color(ax.fill_between, hue=None, color=None, kws=kws)
    assert color == to_rgb("#1f77b4")


def test_default_color_on_fill_between():
    f, ax = plt.subplots()
    kws = {}
    color = utils._default_color(ax.fill_between, hue=None, color=None, kws=kws)
    assert color == to_rgb("#1f77b4")


def test_default_color_on_fill_between():
    f, ax = plt.subplots()
    kws = {}
    color = utils._default_color(ax.fill_between, hue=None, color=None, kws=kws)
    assert color == to_rgb("#1f77b4")


def test_default_color_on_fill_between():
    f, ax = plt.subplots()
    kws = {}
    color = utils._default_color(ax.fill_between, hue=None, color=None, kws=kws)
    assert color == to_rgb("#1f77b4")


def test_default_color_on_fill_between():
    f, ax = plt.subplots()
    kws = {}
    color = utils._default_color(ax.fill_between, hue=None, color=None, kws=kws)
    assert color == to_rgb("#1f77b4")


def test_default_color_on_fill_between():
    f, ax = plt.subplots()
    kws = {}
    color = utils._default_color(ax.fill_between, hue=None, color=None, kws=kws)
    assert color == to_rgb("#1f77b4")


def test_default_color_on_fill_between():
    f, ax = plt.subplots()
    kws = {}
    color = utils._default_color(ax.fill_between, hue=None, color=None, kws=kws)
    assert color == to_rgb("#1f77b4")


def test_default_color_on_fill_between():
    f, ax = plt.subplots()
    kws = {}
    color = utils._default_color(ax.fill_between, hue=None, color=None, kws=kws)
    assert color == to_rgb("#1f77b4")


def test_default_color_on_fill_between():
    f, ax = plt.subplots()
    kws = {}
    color = utils._default_color(ax.fill_between, hue=None, color=None, kws=kws)
    assert color == to_rgb("#1f77b4")


def test_default_color_on_fill_between():
    f, ax = plt.subplots()
    kws = {}
    color = utils._default_color(ax.fill_between, hue=None, color=None, kws=kws)
    assert color == to_rgb("#1f77b4")


def test_default_color_on_fill_between():
    f, ax = plt.subplots()
    kws = {}
    color = utils._default_color(ax.fill_between, hue=None, color=None, kws=kws)
    assert color == to_rgb("#1f77b4")


def test_default_color_on_fill_between():
    f, ax = plt.subplots()
    kws = {}
    color = utils._default_color(ax.fill_between, hue=None, color=None, kws=kws)
    assert color == to_rgb("#1f77b4")


def test_default_color_on_fill_between():
    f, ax = plt.subplots()
    kws = {}
    color = utils._default_color(ax.fill_between, hue=None, color=None, kws=kws)
    assert color == to_rgb("#1f77b4")


def test_default_color_on_fill_between():
    f, ax = plt.subplots()
    kws = {}
    color = utils._default_color(ax.fill_between, hue=None, color=None, kws=kws)
    assert color == to_rgb("#1f77b4")


def test_default_color_on_fill_between():
    f, ax = plt.subplots()
    kws = {}
    color = utils._default_color(ax.fill_between, hue=None, color=None, kws=kws)
    assert color == to_rgb("#1f77b4")


def test_default_color_on_fill_between():
    f, ax = plt.subplots()
    kws = {}
    color = utils._default_color(ax.fill_between, hue=None, color=None, kws=kws)
    assert color == to_rgb("#1f77b4")


def test_default_color_on_fill_between():
    f, ax = plt.subplots()
    kws = {}
    color = utils._default_color(ax.fill_between, hue=None, color=None, kws=kws)
    assert color == to_rgb("#1f77b4")


def test_default_color_on_fill_between():
    f, ax = plt.subplots()
    kws = {}
    color = utils._default_color(ax.fill_between, hue=None, color=None, kws=kws)
    assert color == to_rgb("#1f77b4")


def test_default_color_on_fill_between():
    f, ax = plt.subplots()
    kws = {}
    color = utils._default_color(ax.fill_between, hue=None, color=None, kws=kws)
    assert color == to_rgb("#1f77b4")


def test_default_color_on_fill_between():
    f, ax = plt.subplots()
    kws = {}
    color = utils._default_color(ax.fill_between, hue=None, color=None, kws=kws)
    assert color == to_rgb("#1f77b4")


def test_default_color_on_fill_between():
    f, ax = plt.subplots()
    kws = {}
    color = utils._default_color(ax.fill_between, hue=None, color=None, kws=kws)
    assert color == to_rgb("#1f77b4")


def test_default_color_on_fill_between():
    f, ax = plt.subplots()
    kws = {}
    color = utils._default_color(ax.fill_between, hue=None, color=None, kws=kws)
    assert color == to_rgb("#1f77b4")


def test_default_color_on_fill_between():
    f, ax = plt.subplots()
    kws = {}
    color = utils._default_color(ax.fill_between, hue=None, color=None, kws=kws)
    assert color == to_rgb("#1f77b4")


def test_default_color_on_fill_between():
    f, ax = plt.subplots()
    kws = {}
    color = utils._default_color(ax.fill_between, hue=None, color=None, kws=kws)
    assert color == to_rgb("#1f77b4")


def test_default_color_on_fill_between():
    f, ax = plt.subplots()
    kws = {}
    color = utils._default_color(ax.fill_between, hue=None, color=None, kws=kws)
    assert color == to_rgb("#1f77b4")


def test_default_color_on_fill_between():
    f, ax = plt.subplots()
    kws = {}
    color = utils._default_color(ax.fill_between, hue=None, color=None, kws=kws)
    assert color == to_rgb("#1f77b4")


def test_default_color_on_fill_between():
    f, ax = plt.subplots()
    kws = {}
    color = utils._default_color(ax.fill_between, hue=None, color=None, kws=kws)
    assert color == to_rgb("#1f77b4")


def test_default_color_on_fill_between():
    f, ax = plt.subplots()
    kws = {}
    color = utils._default_color(ax.fill_between, hue=None, color=None, kws=kws)
    assert color == to_rgb("#1f77b4")


def test_default_color_on_fill_between():
    f, ax = plt.subplots()
    kws = {}
    color = utils._default_color(ax.fill_between, hue=None, color=None, kws=kws)
    assert color == to_rgb("#1f77b4")


def test_default_color_on_fill_between():
    f, ax = plt.subplots()
    kws = {}
    color = utils._default_color(ax.fill_between, hue=None, color=None, kws=kws)
    assert color == to_rgb("#1f77b4")


def test_default_color_on_fill_between():
    f, ax = plt.subplots()
    kws = {}
    color = utils._default_color(ax.fill_between, hue=None, color=None, kws=kws)
    assert color == to_rgb("#1f77b4")


def test_default_color_on_fill_between():
    f, ax = plt.subplots()
    kws = {}
    color = utils._default_color(ax.fill_between, hue=None, color=None, kws=kws)
    assert color == to_rgb("#1f77b4")


def test_default_color_on_fill_between():
    f, ax = plt.subplots()
    kws = {}
    color = utils._default_color(ax.fill_between, hue=None, color=None, kws=kws)
    assert color == to_rgb("#1f77b4")


def test_default_color_on_fill_between():
    f, ax = plt.subplots()
    kws = {}
    color = utils._default_color(ax.fill_between, hue=None, color=None, kws=kws)
    assert color == to_rgb("#1f77b4")


def test_default_color_on_fill_between():
    f, ax = plt.subplots()
    kws = {}
    color = utils._default_color(ax.fill_between, hue=None, color=None, kws=kws)
    assert color == to_rgb("#1f77b4")


def test_default_color_on_fill_between():
    f, ax = plt.subplots()
    kws = {}
    color = utils._default_color(ax.fill_between, hue=None, color=None, kws=kws)
    assert color == to_rgb("#1f77b4")


def test_default_color_on_fill_between():
    f, ax = plt.subplots()
    kws = {}
    color = utils._default_color(ax.fill_between, hue=None, color=None, kws=kws)
    assert color == to_rgb("#1f77b4")


def test_default_color_on_fill_between():
    f, ax = plt.subplots()
    kws = {}
    color = utils._default_color(ax.fill_between, hue=None, color=None, kws=kws)
    assert color == to_rgb("#1f77b4")


def test_default_color_on_fill_between():
    f, ax = plt.subplots()
    kws = {}
    color = utils._default_color(ax.fill_between, hue=None, color=None, kws=kws)
    assert color == to_rgb("#1f77b4")


def test_default_color_on_fill_between():
    f, ax = plt.subplots()
    kws = {}
    color = utils._default_color(ax.fill_between, hue=None, color=None, kws=kws)
    assert color == to_rgb("#1f77b4")


def test_default_color_on_fill_between():
    f, ax = plt.subplots()
    kws = {}
    color = utils._default_color(ax.fill_between, hue=None, color=None, kws=kws)
    assert color == to_rgb("#1f77b4")


def test_default_color_on_fill_between():
    f, ax = plt.subplots()
    kws = {}
    color = utils._default_color(ax.fill_between, hue=None, color=None, kws=kws)
    assert color == to_rgb("#1f77b4")


def test_default_color_on_fill_between():
    f, ax = plt.subplots()
    kws = {}
    color = utils._default_color(ax.fill_between, hue=None, color=None, kws=kws)
    assert color == to_rgb("#1f77b4")


def test_default_color_on_fill_between():
    f, ax = plt.subplots()
    kws = {}
    color = utils._default_color(ax.fill_between, hue=None, color=None, kws=kws)
    assert color == to_rgb("#1f77b4")


def test_default_color_on_fill_between():
    f, ax = plt.subplots()
    kws = {}
    color = utils._default_color(ax.fill_between, hue=None, color=None, kws=kws)
    assert color == to_rgb("#1f77b4")


def test_default_color_on_fill_between():
    f, ax = plt.subplots()
    kws = {}
    color = utils._default_color(ax.fill_between, hue=None, color=None, kws=kws)
    assert color == to_rgb("#1f77b4")


def test_default_color_on_fill_between():
    f, ax = plt.subplots()
    kws = {}
    color = utils._default_color(ax.fill_between, hue=None, color=None, kws=kws)
    assert color == to_rgb("#1f77b4")


def test_default_color_on_fill_between():
    f, ax = plt.subplots()
    kws = {}
    color = utils._default_color(ax.fill_between, hue=None, color=None, kws=kws)
    assert color == to_rgb("#1f77b4")


def test_default_color_on_fill_between():
    f, ax = plt.subplots()
    kws = {}
    color = utils._default_color(ax.fill_between, hue=None, color=None, kws=kws)
    assert color == to_rgb("#1f77b4")


def test_default_color_on_fill_between():
    f, ax = plt.subplots()
    kws = {}
    color = utils._default_color(ax.fill_between, hue=None, color=None, kws=kws)
    assert color == to_rgb("#1f77b4")


def test_default_color_on_fill_between():
    f, ax = plt.subplots()
    kws = {}
    color = utils._default_color(ax.fill_between, hue=None, color=None, kws=kws)
    assert color == to_rgb("#1f77b4")


def test_default_color_on_fill_between():
    f, ax = plt.subplots()
    kws = {}
    color = utils._default_color(ax.fill_between, hue=None, color=None, kws=kws)
    assert color == to_rgb("#1f77b4")


def test_default_color_on_fill_between():
    f, ax = plt.subplots()
    kws = {}
    color = utils._default_color(ax.fill_between, hue=None, color=None, kws=kws)
    assert color == to_rgb("#1f77b4")


def test_default_color_on_fill_between():
    f, ax = plt.subplots()
    kws = {}
    color = utils._default_color(ax.fill_between, hue=None, color=None, kws=kws)
    assert color == to_rgb("#1f77b4")


def test_default_color_on_fill_between():
    f, ax = plt.subplots()
    kws = {}
    color = utils._default_color(ax.fill_between, hue=None, color=None, kws=kws)
    assert color == to_rgb("#1f77b4")


def test_default_color_on_fill_between():
    f, ax = plt.subplots()
    kws = {}
    color = utils._default_color(ax.fill_between, hue=None, color=None, kws=kws)
    assert color == to_rgb("#1f77b4")


def test_default_color_on_fill_between():
    f, ax = plt.subplots()
    kws = {}
    color = utils._default_color(ax.fill_between, hue=None, color=None, kws=kws)
    assert color == to_rgb("#1f77b4")


def test_default_color_on_fill_between():
    f, ax = plt.subplots()
    kws = {}
    color = utils._default_color(ax.fill_between, hue=None, color=None, kws=kws)
    assert color == to_rgb("#1f77b4")


def test_default_color_on_fill_between():
    f, ax = plt.subplots()
    kws = {}
    color = utils._default_color(ax.fill_between, hue=None, color=None, kws=kws)
    assert color == to_rgb("#1f77b4")


def test_default_color_on_fill_between():
    f, ax = plt.subplots()
    kws = {}
    color = utils._default_color(ax.fill_between, hue=None, color=None, kws=kws)
    assert color == to_rgb("#1f77b4")


def test_default_color_on_fill_between():
    f, ax = plt.subplots()
    kws = {}
    color = utils._default_color(ax.fill_between, hue=None, color=None, kws=kws)
    assert color == to_rgb("#1f77b4")


def test_default_color_on_fill_between():
    f, ax = plt.subplots()
    kws = {}
    color = utils._default_color(ax.fill_between, hue=None, color=None, kws=kws)
    assert color == to_rgb("#1f77b4")


def test_default_color_on_fill_between():
    f, ax = plt.subplots()
    kws = {}
    color = utils._default_color(ax.fill_between, hue=None, color=None, kws=kws)
    assert color == to_rgb("#1f77b4")


def test_default_color_on_fill_between():
    f, ax = plt.subplots()
    kws = {}
    color = utils._default_color(ax.fill_between, hue=None, color=None, kws=kws)
    assert color == to_rgb("#1f77b4")


def test_default_color_on_fill_between():
    f, ax = plt.subplots()
    kws = {}
    color = utils._default_color(ax.fill_between, hue=None, color=None, kws=kws)
    assert color == to_rgb("#1f77b4")


def test_default_color_on_fill_between():
    f, ax = plt.subplots()
    kws = {}
    color = utils._default_color(ax.fill_between, hue=None, color=None, kws=kws)
    assert color == to_rgb("#1f77b4")


def test_default_color_on_fill_between():
    f, ax = plt.subplots()
    kws = {}
    color = utils._default_color(ax.fill_between, hue=None, color=None, kws=kws)
    assert color == to_rgb("#1f77b4")


def test_default_color_on_fill_between():
    f, ax = plt.subplots()
    kws = {}
    color = utils._default_color(ax.fill_between, hue=None, color=None, kws=kws)
    assert color == to_rgb("#1f77b4")


def test_default_color_on_fill_between():
    f, ax = plt.subplots()
    kws = {}
    color = utils._default_color(ax.fill_between, hue=None, color=None, kws=kws)
    assert color == to_rgb("#1f77b4")


def test_default_color_on_fill_between():
    f, ax = plt.subplots()
    kws = {}
    color = utils._default_color(ax.fill_between, hue=None, color=None, kws=kws)
    assert color == to_rgb("#1f77b4")


def test_default_color_on_fill_between():
    f, ax = plt.subplots()
    kws = {}
    color = utils._default_color(ax.fill_between, hue=None, color=None, kws=kws)
    assert color == to_rgb("#1f77b4")


def test_default_color_on_fill_between():
    f, ax = plt.subplots()
    kws = {}
    color = utils._default_color(ax.fill_between, hue=None, color=None, kws=kws)
    assert color == to_rgb("#1f77b4")


def test_default_color_on_fill_between():
    f, ax = plt.subplots()
    kws = {}
    color = utils._default_color(ax.fill_between, hue=None, color=None, kws=kws)
    assert color == to_rgb("#1f77b4")


def test_default_color_on_fill_between():
    f, ax = plt.subplots()
    kws = {}
    color = utils._default_color(ax.fill_between, hue=None, color=None, kws=kws)
    assert color == to_rgb("#1f77b4")


def test_default_color_on_fill_between():
    f, ax = plt.subplots()
    kws = {}
    color = utils._default_color(ax.fill_between, hue=None, color=None, kws=kws)
    assert color == to_rgb("#1f77b4")


def test_default_color_on_fill_between():
    f, ax = plt.subplots()
    kws = {}
    color = utils._default_color(ax.fill_between, hue=None, color=None, kws=kws)
    assert color == to_rgb("#1f77b4")


def test_default_color_on_fill_between():
    f, ax = plt.subplots()
    kws = {}
    color = utils._default_color(ax.fill_between, hue=None, color=None, kws=kws)
    assert color == to_rgb("#1f77b4")


def test_default_color_on_fill_between():
    f, ax = plt.subplots()
    kws = {}
    color = utils._default_color(ax.fill_between, hue=None, color=None, kws=kws)
    assert color == to_rgb("#1f77b4")


def test_set_color_codes():
    """Test the high-level set color codes function."""
    set_color_codes()
    assert palettes.color_palette()[2] == palettes.COLOR_PALETTE["b"]
    set_color_codes("deep")
    assert palettes.color_palette()[2] == palettes.COLOR_PALETTE["b"]
    set_color_codes("muted")
    assert palettes.color_palette()[2] == palettes.COLOR_PALETTE["g"]


def test_despine():
    """Test despine function."""
    f = plt.figure()
    ax = f.add_subplot(111)

    sns.despine()
    assert not ax.spines["top"].get_visible()
    assert not ax.spines["right"].get_visible()
    assert ax.spines["left"].get_visible()
    assert ax.spines["bottom"].get_visible()

    ax = f.add_subplot(222, polar=True)
    sns.despine(ax=ax)
    assert ax.spines["top"].get_visible()
    assert ax.spines["right"].get_visible()
    assert ax.spines["left"].get_visible()
    assert ax.spines["bottom"].get_visible()

    sns.despine(offset=2)
    assert ax.spines["top"].get_visible()
    assert ax.spines["right"].get_visible()
    assert ax.spines["left"].get_visible()
    assert ax.spines["bottom"].get_visible()


def test_despine_trim():
    """Test despine trim option."""
    f, ax = plt.subplots()
    ax.scatter(range(10), range(10))
    ax.set_xticks([0, 5, 9])
    sns.despine(trim=True)
    assert tuple(ax.spines["bottom"].get_bounds()) == (0, 9)
    plt.close(f)


def test_move_legend():
    f, ax = plt.subplots()

    # Draw points
    x = np.arange(10)
    y = np.random.rand(10)
    ax.scatter(x, y, label="a")

    # Draw legend
    ax.legend()

    # Ensure the legend is attached to the axes
    assert ax.legend_ is not None

    # Move the legend
    sns.move_legend(ax, "upper right")

    # Ensure the moved legend is attached to the axes
    assert ax.legend_ is not None


def test_move_legend():
    f, ax = plt.subplots()

    # Draw points
    x = np.arange(10)
    y = np.random.rand(10)
    ax.scatter(x, y, label="a")

    # Draw legend
    ax.legend()

    # Ensure the legend is attached to the axes
    assert ax.legend_ is not None

    # Move the legend
    sns.move_legend(ax, "upper right")

    # Ensure the moved legend is attached to the axes
    assert ax.legend_ is not None


def test_move_legend():
    f, ax = plt.subplots()

    # Draw points
    x = np.arange(10)
    y = np.random.rand(10)
    ax.scatter(x, y, label="a")

    # Draw legend
    ax.legend()

    # Ensure the legend is attached to the axes
    assert ax.legend_ is not None

    # Move the legend
    sns.move_legend(ax, "upper right")

    # Ensure the moved legend is attached to the axes
    assert ax.legend_ is not None


def test_move_legend():
    f, ax = plt.subplots()

    # Draw points
    x = np.arange(10)
    y = np.random.rand(10)
    ax.scatter(x, y, label="a")

    # Draw legend
    ax.legend()

    # Ensure the legend is attached to the axes
    assert ax.legend_ is not None

    # Move the legend
    sns.move_legend(ax, "upper right")

    # Ensure the moved legend is attached to the axes
    assert ax.legend_ is not None


def test_move_legend():
    f, ax = plt.subplots()

    # Draw points
    x = np.arange(10)
    y = np.random.rand(10)
    ax.scatter(x, y, label="a")

    # Draw legend
    ax.legend()

    # Ensure the legend is attached to the axes
    assert ax.legend_ is not None

    # Move the legend
    sns.move_legend(ax, "upper right")

    # Ensure the moved legend is attached to the axes
    assert ax.legend_ is not None


def test_move_legend():
    f, ax = plt.subplots()

    # Draw points
    x = np.arange(10)
    y = np.random.rand(10)
    ax.scatter(x, y, label="a")

    # Draw legend
    ax.legend()

    # Ensure the legend is attached to the axes
    assert ax.legend_ is not None

    # Move the legend
    sns.move_legend(ax, "upper right")

    # Ensure the moved legend is attached to the axes
    assert ax.legend_ is not None


def test_move_legend():
    f, ax = plt.subplots()

    # Draw points
    x = np.arange(10)
    y = np.random.rand(10)
    ax.scatter(x, y, label="a")

    # Draw legend
    ax.legend()

    # Ensure the legend is attached to the axes
    assert ax.legend_ is not None

    # Move the legend
    sns.move_legend(ax, "upper right")

    # Ensure the moved legend is attached to the axes
    assert ax.legend_ is not None


def test_move_legend():
    f, ax = plt.subplots()

    # Draw points
    x = np.arange(10)
    y = np.random.rand(10)
    ax.scatter(x, y, label="a")

    # Draw legend
    ax.legend()

    # Ensure the legend is attached to the axes
    assert ax.legend_ is not None

    # Move the legend
    sns.move_legend(ax, "upper right")

    # Ensure the moved legend is attached to the axes
    assert ax.legend_ is not None


def test_move_legend():
    f, ax = plt.subplots()

    # Draw points
    x = np.arange(10)
    y = np.random.rand(10)
    ax.scatter(x, y, label="a")

    # Draw legend
    ax.legend()

    # Ensure the legend is attached to the axes
    assert ax.legend_ is not None

    # Move the legend
    sns.move_legend(ax, "upper right")

    # Ensure the moved legend is attached to the axes
    assert ax.legend_ is not None


def test_move_legend():
    f, ax = plt.subplots()

    # Draw points
    x = np.arange(10)
    y = np.random.rand(10)
    ax.scatter(x, y, label="a")

    # Draw legend
    ax.legend()

    # Ensure the legend is attached to the axes
    assert ax.legend_ is not None

    # Move the legend
    sns.move_legend(ax, "upper right")

    # Ensure the moved legend is attached to the axes
    assert ax.legend_ is not None


def test_move_legend():
    f, ax = plt.subplots()

    # Draw points
    x = np.arange(10)
    y = np.random.rand(10)
    ax.scatter(x, y, label="a")

    # Draw legend
    ax.legend()

    # Ensure the legend is attached to the axes
    assert ax.legend_ is not None

    # Move the legend
    sns.move_legend(ax, "upper right")

    # Ensure the moved legend is attached to the axes
    assert ax.legend_ is not None


def test_move_legend():
    f, ax = plt.subplots()

    # Draw points
    x = np.arange(10)
    y = np.random.rand(10)
    ax.scatter(x, y, label="a")

    # Draw legend
    ax.legend()

    # Ensure the legend is attached to the axes
    assert ax.legend_ is not None

    # Move the legend
    sns.move_legend(ax, "upper right")

    # Ensure the moved legend is attached to the axes
    assert ax.legend_ is not None


def test_move_legend():
    f, ax = plt.subplots()

    # Draw points
    x = np.arange(10)
    y = np.random.rand(10)
    ax.scatter(x, y, label="a")

    # Draw legend
    ax.legend()

    # Ensure the legend is attached to the axes
    assert ax.legend_ is not None

    # Move the legend
    sns.move_legend(ax, "upper right")

    # Ensure the moved legend is attached to the axes
    assert ax.legend_ is not None


def test_move_legend():
    f, ax = plt.subplots()

    # Draw points
    x = np.arange(10)
    y = np.random.rand(10)
    ax.scatter(x, y, label="a")

    # Draw legend
    ax.legend()

    # Ensure the legend is attached to the axes
    assert ax.legend_ is not None

    # Move the legend
    sns.move_legend(ax, "upper right")

    # Ensure the moved legend is attached to the axes
    assert ax.legend_ is not None


def test_move_legend():
    f, ax = plt.subplots()

    # Draw points
    x = np.arange(10)
    y = np.random.rand(10)
    ax.scatter(x, y, label="a")

    # Draw legend
    ax.legend()

    # Ensure the legend is attached to the axes
    assert ax.legend_ is not None

    # Move the legend
    sns.move_legend(ax, "upper right")

    # Ensure the moved legend is attached to the axes
    assert ax.legend_ is not None


def test_move_legend():
    f, ax = plt.subplots()

    # Draw points
    x = np.arange(10)
    y = np.random.rand(10)
    ax.scatter(x, y, label="a")

    # Draw legend
    ax.legend()

    # Ensure the legend is attached to the axes
    assert ax.legend_ is not None

    # Move the legend
    sns.move_legend(ax, "upper right")

    # Ensure the moved legend is attached to the axes
    assert ax.legend_ is not None


def test_move_legend():
    f, ax = plt.subplots()

    # Draw points
    x = np.arange(10)
    y = np.random.rand(10)
    ax.scatter(x, y, label="a")

    # Draw legend
    ax.legend()

    # Ensure the legend is attached to the axes
    assert ax.legend_ is not None

    # Move the legend
    sns.move_legend(ax, "upper right")

    # Ensure the moved legend is attached to the axes
    assert ax.legend_ is not None


def test_move_legend():
    f, ax = plt.subplots()

    # Draw points
    x = np.arange(10)
    y = np.random.rand(10)
    ax.scatter(x, y, label="a")

    # Draw legend
    ax.legend()

    # Ensure the legend is attached to the axes
    assert ax.legend_ is not None

    # Move the legend
    sns.move_legend(ax, "upper right")

    # Ensure the moved legend is attached to the axes
    assert ax.legend_ is not None


def test_move_legend():
    f, ax = plt.subplots()

    # Draw points
    x = np.arange(10)
    y = np.random.rand(10)
    ax.scatter(x, y, label="a")

    # Draw legend
    ax.legend()

    # Ensure the legend is attached to the axes
    assert ax.legend_ is not None

    # Move the legend
    sns.move_legend(ax, "upper right")

    # Ensure the moved legend is attached to the axes
    assert ax.legend_ is not None


def test_move_legend():
    f, ax = plt.subplots()

    # Draw points
    x = np.arange(10)
    y = np.random.rand(10)
    ax.scatter(x, y, label="a")

    # Draw legend
    ax.legend()

    # Ensure the legend is attached to the axes
    assert ax.legend_ is not None

    # Move the legend
    sns.move_legend(ax, "upper right")

    # Ensure the moved legend is attached to the axes
    assert ax.legend_ is not None


def test_move_legend():
    f, ax = plt.subplots()

    # Draw points
    x = np.arange(10)
    y = np.random.rand(10)
    ax.scatter(x, y, label="a")

    # Draw legend
    ax.legend()

    # Ensure the legend is attached to the axes
    assert ax.legend_ is not None

    # Move the legend
    sns.move_legend(ax, "upper right")

    # Ensure the moved legend is attached to the axes
    assert ax.legend_ is not None


def test_move_legend():
    f, ax = plt.subplots()

    # Draw points
    x = np.arange(10)
    y = np.random.rand(10)
    ax.scatter(x, y, label="a")

    # Draw legend
    ax.legend()

    # Ensure the legend is attached to the axes
    assert ax.legend_ is not None

    # Move the legend
    sns.move_legend(ax, "upper right")

    # Ensure the moved legend is attached to the axes
    assert ax.legend_ is not None


def test_move_legend():
    f, ax = plt.subplots()

    # Draw points
    x = np.arange(10)
    y = np.random.rand(10)
    ax.scatter(x, y, label="a")

    # Draw legend
    ax.legend()

    # Ensure the legend is attached to the axes
    assert ax.legend_ is not None

    # Move the legend
    sns.move_legend(ax, "upper right")

    # Ensure the moved legend is attached to the axes
    assert ax.legend_ is not None


def test_move_legend():
    f, ax = plt.subplots()

    # Draw points
    x = np.arange(10)
    y = np.random.rand(10)
    ax.scatter(x, y, label="a")

    # Draw legend
    ax.legend()

    # Ensure the legend is attached to the axes
    assert ax.legend_ is not None

    # Move the legend
    sns.move_legend(ax, "upper right")

    # Ensure the moved legend is attached to the axes
    assert ax.legend_ is not None


def test_move_legend():
    f, ax = plt.subplots()

    # Draw points
    x = np.arange(10)
    y = np.random.rand(10)
    ax.scatter(x, y, label="a")

    # Draw legend
    ax.legend()

    # Ensure the legend is attached to the axes
    assert ax.legend_ is not None

    # Move the legend
    sns.move_legend(ax, "upper right")

    # Ensure the moved legend is attached to the axes
    assert ax.legend_ is not None


def test_move_legend():
    f, ax = plt.subplots()

    # Draw points
    x = np.arange(10)
    y = np.random.rand(10)
    ax.scatter(x, y, label="a")

    # Draw legend
    ax.legend()

    # Ensure the legend is attached to the axes
    assert ax.legend_ is not None

    # Move the legend
    sns.move_legend(ax, "upper right")

    # Ensure the moved legend is attached to the axes
    assert ax.legend_ is not None


def test_move_legend():
    f, ax = plt.subplots()

    # Draw points
    x = np.arange(10)
    y = np.random.rand(10)
    ax.scatter(x, y, label="a")

    # Draw legend
    ax.legend()

    # Ensure the legend is attached to the axes
    assert ax.legend_ is not None

    # Move the legend
    sns.move_legend(ax, "upper right")

    # Ensure the moved legend is attached to the axes
    assert ax.legend_ is not None


def test_move_legend():
    f, ax = plt.subplots()

    # Draw points
    x = np.arange(10)
    y = np.random.rand(10)
    ax.scatter(x, y, label="a")

    # Draw legend
    ax.legend()

    # Ensure the legend is attached to the axes
    assert ax.legend_ is not None

    # Move the legend
    sns.move_legend(ax, "upper right")

    # Ensure the moved legend is attached to the axes
    assert ax.legend_ is not None


def test_move_legend():
    f, ax = plt.subplots()

    # Draw points
    x = np.arange(10)
    y = np.random.rand(10)
    ax.scatter(x, y, label="a")

    # Draw legend
    ax.legend()

    # Ensure the legend is attached to the axes
    assert ax.legend_ is not None

    # Move the legend
    sns.move_legend(ax, "upper right")

    # Ensure the moved legend is attached to the axes
    assert ax.legend_ is not None


def test_move_legend():
    f, ax = plt.subplots()

    # Draw points
    x = np.arange(10)
    y = np.random.rand(10)
    ax.scatter(x, y, label="a")

    # Draw legend
    ax.legend()

    # Ensure the legend is attached to the axes
    assert ax.legend_ is not None

    # Move the legend
    sns.move_legend(ax, "upper right")

    # Ensure the moved legend is attached to the axes
    assert ax.legend_ is not None


def test_move_legend():
    f, ax = plt.subplots()

    # Draw points
    x = np.arange(10)
    y = np.random.rand(10)
    ax.scatter(x, y, label="a")

    # Draw legend
    ax.legend()

    # Ensure the legend is attached to the axes
    assert ax.legend_ is not None

    # Move the legend
    sns.move_legend(ax, "upper right")

    # Ensure the moved legend is attached to the axes
    assert ax.legend_ is not None


def test_move_legend():
    f, ax = plt.subplots()

    # Draw points
    x = np.arange(10)
    y = np.random.rand(10)
    ax.scatter(x, y, label="a")

    # Draw legend
    ax.legend()

    # Ensure the legend is attached to the axes
    assert ax.legend_ is not None

    # Move the legend
    sns.move_legend(ax, "upper right")

    # Ensure the moved legend is attached to the axes
    assert ax.legend_ is not None


def test_move_legend():
    f, ax = plt.subplots()

    # Draw points
    x = np.arange(10)
    y = np.random.rand(10)
    ax.scatter(x, y, label="a")

    # Draw legend
    ax.legend()

    # Ensure the legend is attached to the axes
    assert ax.legend_ is not None

    # Move the legend
    sns.move_legend(ax, "upper right")

    # Ensure the moved legend is attached to the axes
    assert ax.legend_ is not None


def test_move_legend():
    f, ax = plt.subplots()

    # Draw points
    x = np.arange(10)
    y = np.random.rand(10)
    ax.scatter(x, y, label="a")

    # Draw legend
    ax.legend()

    # Ensure the legend is attached to the axes
    assert ax.legend_ is not None

    # Move the legend
    sns.move_legend(ax, "upper right")

    # Ensure the moved legend is attached to the axes
    assert ax.legend_ is not None


def test_move_legend():
    f, ax = plt.subplots()

    # Draw points
    x = np.arange(10)
    y = np.random.rand(10)
    ax.scatter(x, y, label="a")

    # Draw legend
    ax.legend()

    # Ensure the legend is attached to the axes
    assert ax.legend_ is not None

    # Move the legend
    sns.move_legend(ax, "upper right")

    # Ensure the moved legend is attached to the axes
    assert ax.legend_ is not None


def test_move_legend():
    f, ax = plt.subplots()

    # Draw points
    x = np.arange(10)
    y = np.random.rand(10)
    ax.scatter(x, y, label="a")

    # Draw legend
    ax.legend()

    # Ensure the legend is attached to the axes
    assert ax.legend_ is not None

    # Move the legend
    sns.move_legend(ax, "upper right")

    # Ensure the moved legend is attached to the axes
    assert ax.legend_ is not None


def test_move_legend():
    f, ax = plt.subplots()

    # Draw points
    x = np.arange(10)
    y = np.random.rand(10)
    ax.scatter(x, y, label="a")

    # Draw legend
    ax.legend()

    # Ensure the legend is attached to the axes
    assert ax.legend_ is not None

    # Move the legend
    sns.move_legend(ax, "upper right")

    # Ensure the moved legend is attached to the axes
    assert ax.legend_ is not None


def test_move_legend():
    f, ax = plt.subplots()

    # Draw points
    x = np.arange(10)
    y = np.random.rand(10)
    ax.scatter(x, y, label="a")

    # Draw legend
    ax.legend()

    # Ensure the legend is attached to the axes
    assert ax.legend_ is not None

    # Move the legend
    sns.move_legend(ax, "upper right")

    # Ensure the moved legend is attached to the axes
    assert ax.legend_ is not None


def test_move_legend():
    f, ax = plt.subplots()

    # Draw points
    x = np.arange(10)
    y = np.random.rand(10)
    ax.scatter(x, y, label="a")

    # Draw legend
    ax.legend()

    # Ensure the legend is attached to the axes
    assert ax.legend_ is not None

    # Move the legend
    sns.move_legend(ax, "upper right")

    # Ensure the moved legend is attached to the axes
    assert ax.legend_ is not None


def test_move_legend():
    f, ax = plt.subplots()

    # Draw points
    x = np.arange(10)
    y = np.random.rand(10)
    ax.scatter(x, y, label="a")

    # Draw legend
    ax.legend()

    # Ensure the legend is attached to the axes
    assert ax.legend_ is not None

    # Move the legend
    sns.move_legend(ax, "upper right")

    # Ensure the moved legend is attached to the axes
    assert ax.legend_ is not None


def test_move_legend():
    f, ax = plt.subplots()

    # Draw points
    x = np.arange(10)
    y = np.random.rand(10)
    ax.scatter(x, y, label="a")

    # Draw legend
    ax.legend()

    # Ensure the legend is attached to the axes
    assert ax.legend_ is not None

    # Move the legend
    sns.move_legend(ax, "upper right")

    # Ensure the moved legend is attached to the axes
    assert ax.legend_ is not None


def test_move_legend():
    f, ax = plt.subplots()

    # Draw points
    x = np.arange(10)
    y = np.random.rand(10)
    ax.scatter(x, y, label="a")

    # Draw legend
    ax.legend()

    # Ensure the legend is attached to the axes
    assert ax.legend_ is not None

    # Move the legend
    sns.move_legend(ax, "upper right")

    # Ensure the moved legend is attached to the axes
    assert ax.legend_ is not None


def test_move_legend():
    f, ax = plt.subplots()

    # Draw points
    x = np.arange(10)
    y = np.random.rand(10)
    ax.scatter(x, y, label="a")

    # Draw legend
    ax.legend()

    # Ensure the legend is attached to the axes
    assert ax.legend_ is not None

    # Move the legend
    sns.move_legend(ax, "upper right")

    # Ensure the moved legend is attached to the axes
    assert ax.legend_ is not None


def test_move_legend():
    f, ax = plt.subplots()

    # Draw points
    x = np.arange(10)
    y = np.random.rand(10)
    ax.scatter(x, y, label="a")

    # Draw legend
    ax.legend()

    # Ensure the legend is attached to the axes
    assert ax.legend_ is not None

    # Move the legend
    sns.move_legend(ax, "upper right")

    # Ensure the moved legend is attached to the axes
    assert ax.legend_ is not None


def test_move_legend():
    f, ax = plt.subplots()

    # Draw points
    x = np.arange(10)
    y = np.random.rand(10)
    ax.scatter(x, y, label="a")

    # Draw legend
    ax.legend()

    # Ensure the legend is attached to the axes
    assert ax.legend_ is not None

    # Move the legend
    sns.move_legend(ax, "upper right")

    # Ensure the moved legend is attached to the axes
    assert ax.legend_ is not None


def test_move_legend():
    f, ax = plt.subplots()

    # Draw points
    x = np.arange(10)
    y = np.random.rand(10)
    ax.scatter(x, y, label="a")

    # Draw legend
    ax.legend()

    # Ensure the legend is attached to the axes
    assert ax.legend_ is not None

    # Move the legend
    sns.move_legend(ax, "upper right")

    # Ensure the moved legend is attached to the axes
    assert ax.legend_ is not None


def test_move_legend():
    f, ax = plt.subplots()

    # Draw points
    x = np.arange(10)
    y = np.random.rand(10)
    ax.scatter(x, y, label="a")

    # Draw legend
    ax.legend()

    # Ensure the legend is attached to the axes
    assert ax.legend_ is not None

    # Move the legend
    sns.move_legend(ax, "upper right")

    # Ensure the moved legend is attached to the axes
    assert ax.legend_ is not None


def test_move_legend():
    f, ax = plt.subplots()

    # Draw points
    x = np.arange(10)
    y = np.random.rand(10)
    ax.scatter(x, y, label="a")

    # Draw legend
    ax.legend()

    # Ensure the legend is attached to the axes
    assert ax.legend_ is not None

    # Move the legend
    sns.move_legend(ax, "upper right")

    # Ensure the moved legend is attached to the axes
    assert ax.legend_ is not None


def test_move_legend():
    f, ax = plt.subplots()

    # Draw points
    x = np.arange(10)
    y = np.random.rand(10)
    ax.scatter(x, y, label="a")

    # Draw legend
    ax.legend()

    # Ensure the legend is attached to the axes
    assert ax.legend_ is not None

    # Move the legend
    sns.move_legend(ax, "upper right")

    # Ensure the moved legend is attached to the axes
    assert ax.legend_ is not None


def test_move_legend():
    f, ax = plt.subplots()

    # Draw points
    x = np.arange(10)
    y = np.random.rand(10)
    ax.scatter(x, y, label="a")

    # Draw legend
    ax.legend()

    # Ensure the legend is attached to the axes
    assert ax.legend_ is not None

    # Move the legend
    sns.move_legend(ax, "upper right")

    # Ensure the moved legend is attached to the axes
    assert ax.legend_ is not None


def test_move_legend():
    f, ax = plt.subplots()

    # Draw points
    x = np.arange(10)
    y = np.random.rand(10)
    ax.scatter(x, y, label="a")

    # Draw legend
    ax.legend()

    # Ensure the legend is attached to the axes
    assert ax.legend_ is not None

    # Move the legend
    sns.move_legend(ax, "upper right")

    # Ensure the moved legend is attached to the axes
    assert ax.legend_ is not None


def test_move_legend():
    f, ax = plt.subplots()

    # Draw points
    x = np.arange(10)
    y = np.random.rand(10)
    ax.scatter(x, y, label="a")

    # Draw legend
    ax.legend()

    # Ensure the legend is attached to the axes
    assert ax.legend_ is not None

    # Move the legend
    sns.move_legend(ax, "upper right")

    # Ensure the moved legend is attached to the axes
    assert ax.legend_ is not None


def test_move_legend():
    f, ax = plt.subplots()

    # Draw points
    x = np.arange(10)
    y = np.random.rand(10)
    ax.scatter(x, y, label="a")

    # Draw legend
    ax.legend()

    # Ensure the legend is attached to the axes
    assert ax.legend_ is not None

    # Move the legend
    sns.move_legend(ax, "upper right")

    # Ensure the moved legend is attached to the axes
    assert ax.legend_ is not None


def test_move_legend():
    f, ax = plt.subplots()

    # Draw points
    x = np.arange(10)
    y = np.random.rand(10)
    ax.scatter(x, y, label="a")

    # Draw legend
    ax.legend()

    # Ensure the legend is attached to the axes
    assert ax.legend_ is not None

    # Move the legend
    sns.move_legend(ax, "upper right")

    # Ensure the moved legend is attached to the axes
    assert ax.legend_ is not None


def test_move_legend():
    f, ax = plt.subplots()

    # Draw points
    x = np.arange(10)
    y = np.random.rand(10)
    ax.scatter(x, y, label="a")

    # Draw legend
    ax.legend()

    # Ensure the legend is attached to the axes
    assert ax.legend_ is not None

    # Move the legend
    sns.move_legend(ax, "upper right")

    # Ensure the moved legend is attached to the axes
    assert ax.legend_ is not None


def test_move_legend():
    f, ax = plt.subplots()

    # Draw points
    x = np.arange(10)
    y = np.random.rand(10)
    ax.scatter(x, y, label="a")

    # Draw legend
    ax.legend()

    # Ensure the legend is attached to the axes
    assert ax.legend_ is not None

    # Move the legend
    sns.move_legend(ax, "upper right")

    # Ensure the moved legend is attached to the axes
    assert ax.legend_ is not None


def test_move_legend():
    f, ax = plt.subplots()

    # Draw points
    x = np.arange(10)
    y = np.random.rand(10)
    ax.scatter(x, y, label="a")

    # Draw legend
    ax.legend()

    # Ensure the legend is attached to the axes
    assert ax.legend_ is not None

    # Move the legend
    sns.move_legend(ax, "upper right")

    # Ensure the moved legend is attached to the axes
    assert ax.legend_ is not None


def test_move_legend():
    f, ax = plt.subplots()

    # Draw points
    x = np.arange(10)
    y = np.random.rand(10)
    ax.scatter(x, y, label="a")

    # Draw legend
    ax.legend()

    # Ensure the legend is attached to the axes
    assert ax.legend_ is not None

    # Move the legend
    sns.move_legend(ax, "upper right")

    # Ensure the moved legend is attached to the axes
    assert ax.legend_ is not None


def test_move_legend():
    f, ax = plt.subplots()

    # Draw points
    x = np.arange(10)
    y = np.random.rand(10)
    ax.scatter(x, y, label="a")

    # Draw legend
    ax.legend()

    # Ensure the legend is attached to the axes
    assert ax.legend_ is not None

    # Move the legend
    sns.move_legend(ax, "upper right")

    # Ensure the moved legend is attached to the axes
    assert ax.legend_ is not None


def test_move_legend():
    f, ax = plt.subplots()

    # Draw points
    x = np.arange(10)
    y = np.random.rand(10)
    ax.scatter(x, y, label="a")

    # Draw legend
    ax.legend()

    # Ensure the legend is attached to the axes
    assert ax.legend_ is not None

    # Move the legend
    sns.move_legend(ax, "upper right")

    # Ensure the moved legend is attached to the axes
    assert ax.legend_ is not None


def test_move_legend():
    f, ax = plt.subplots()

    # Draw points
    x = np.arange(10)
    y = np.random.rand(10)
    ax.scatter(x, y, label="a")

    # Draw legend
    ax.legend()

    # Ensure the legend is attached to the axes
    assert ax.legend_ is not None

    # Move the legend
    sns.move_legend(ax, "upper right")

    # Ensure the moved legend is attached to the axes
    assert ax.legend_ is not None


def test_move_legend():
    f, ax = plt.subplots()

    # Draw points
    x = np.arange(10)
    y = np.random.rand(10)
    ax.scatter(x, y, label="a")

    # Draw legend
    ax.legend()

    # Ensure the legend is attached to the axes
    assert ax.legend_ is not None

    # Move the legend
    sns.move_legend(ax, "upper right")

    # Ensure the moved legend is attached to the axes
    assert ax.legend_ is not None


def test_move_legend():
    f, ax = plt.subplots()

    # Draw points
    x = np.arange(10)
    y = np.random.rand(10)
    ax.scatter(x, y, label="a")

    # Draw legend
    ax