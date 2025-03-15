# SPDX-License-Identifier: BSD-3-Clause

import numpy as np
import pandas as pd
import pytest

from seaborn._core.groupby import GroupBy
from seaborn._core.scales import Nominal, Continuous
from seaborn._stats.counting import Count, Hist

from .. import tools


def test_count():

    var = ["x", "y"]
    data = pd.DataFrame({v: range(3) for v in var})
    groupby = GroupBy(var)
    scales = {v: Nominal() for v in var}

    count = Count()
    results = count(data, groupby, "x", scales)
    assert results.equals(data)

    results = count(data, groupby, "y", scales)
    expected = data.rename(columns={"x": "y", "y": "x"})
    assert results.equals(expected)

    data = pd.concat([data] * 2, ignore_index=True)
    results = count(data, groupby, "x", scales)
    assert results.equals(data)

    results = count(data, groupby, "y", scales)
    assert results.equals(expected)

    data = data.drop([1, 5])
    results = count(data, groupby, "x", scales)
    expected = pd.DataFrame({
        "x": [0, 1, 2, 0, 2],
        "y": [0, 1, 2, 0, 2],
    })
    assert results.equals(expected)

    results = count(data, groupby, "y", scales)
    expected = pd.DataFrame({
        "x": [0, 1, 2, 0, 2],
        "y": [0, 1, 2, 0, 2],
    })[["y", "x"]]
    assert results.equals(expected)


def test_hist_count():

    var = ["x", "y"]
    data = pd.DataFrame({v: range(3) for v in var})
    groupby = GroupBy(var)
    scales = {v: Continuous() for v in var}

    hist = Hist()
    results = hist(data, groupby, "x", scales)
    expected = pd.DataFrame({"x": [0, 1, 2], "count": [1, 1, 1], "space": 1, "y": [1, 1, 1]})
    assert results.equals(expected)

    hist = Hist(discrete=True)
    results = hist(data, groupby, "x", scales)
    expected = pd.DataFrame({"x": [0, 1, 2], "count": [1, 1, 1], "space": 1, "y": [1, 1, 1]})
    assert results.equals(expected)

    hist = Hist(common_bins=False)
    results = hist(data, groupby, "x", scales)
    expected = pd.DataFrame({"x": [0, 1, 2], "count": [1, 1, 1], "space": 1, "y": [1, 1, 1]})
    assert results.equals(expected)

    hist = Hist(common_bins=False, discrete=True)
    results = hist(data, groupby, "x", scales)
    expected = pd.DataFrame({"x": [0, 1, 2], "count": [1, 1, 1], "space": 1, "y": [1, 1, 1]})
    assert results.equals(expected)


def test_hist_density():

    x = np.random.normal(size=100)
    y = np.random.normal(size=100)
    data = pd.DataFrame({"x": x, "y": y})
    groupby = GroupBy(["x", "y"])
    scales = {v: Continuous() for v in ["x", "y"]}

    hist = Hist(stat="density")
    results = hist(data, groupby, "x", scales)
    assert np.isclose(results["x"].sum(), 0, atol=1e-6)
    assert np.isclose(results["y"].sum(), 1, atol=1e-6)

    hist = Hist(stat="density", discrete=True)
    results = hist(data, groupby, "x", scales)
    assert np.isclose(results["x"].sum(), 0, atol=1e-6)
    assert np.isclose(results["y"].sum(), 1, atol=1e-6)

    hist = Hist(stat="density", common_bins=False)
    results = hist(data, groupby, "x", scales)
    assert np.isclose(results["x"].sum(), 0, atol=1e-6)
    assert np.isclose(results["y"].sum(), 1, atol=1e-6)

    hist = Hist(stat="density", common_bins=False, discrete=True)
    results = hist(data, groupby, "x", scales)
    assert np.isclose(results["x"].sum(), 0, atol=1e-6)
    assert np.isclose(results["y"].sum(), 1, atol=1e-6)


def test_hist_percent():

    x = np.random.normal(size=100)
    y = np.random.normal(size=100)
    data = pd.DataFrame({"x": x, "y": y})
    groupby = GroupBy(["x", "y"])
    scales = {v: Continuous() for v in ["x", "y"]}

    hist = Hist(stat="percent")
    results = hist(data, groupby, "x", scales)
    assert np.isclose(results["x"].sum(), 0, atol=1e-6)
    assert np.isclose(results["y"].sum(), 100, atol=1e-6)

    hist = Hist(stat="percent", discrete=True)
    results = hist(data, groupby, "x", scales)
    assert np.isclose(results["x"].sum(), 0, atol=1e-6)
    assert np.isclose(results["y"].sum(), 100, atol=1e-6)

    hist = Hist(stat="percent", common_bins=False)
    results = hist(data, groupby, "x", scales)
    assert np.isclose(results["x"].sum(), 0, atol=1e-6)
    assert np.isclose(results["y"].sum(), 100, atol=1e-6)

    hist = Hist(stat="percent", common_bins=False, discrete=True)
    results = hist(data, groupby, "x", scales)
    assert np.isclose(results["x"].sum(), 0, atol=1e-6)
    assert np.isclose(results["y"].sum(), 100, atol=1e-6)


@pytest.mark.parametrize("stat", ["probability", "proportion"])
def test_hist_probability(stat):

    x = np.random.normal(size=100)
    y = np.random.normal(size=100)
    data = pd.DataFrame({"x": x, "y": y})
    groupby = GroupBy(["x", "y"])
    scales = {v: Continuous() for v in ["x", "y"]}

    hist = Hist(stat=stat)
    results = hist(data, groupby, "x", scales)
    assert np.isclose(results["x"].sum(), 0, atol=1e-6)
    assert np.isclose(results["y"].sum(), 1, atol=1e-6)

    hist = Hist(stat=stat, discrete=True)
    results = hist(data, groupby, "x", scales)
    assert np.isclose(results["x"].sum(), 0, atol=1e-6)
    assert np.isclose(results["y"].sum(), 1, atol=1e-6)

    hist = Hist(stat=stat, common_bins=False)
    results = hist(data, groupby, "x", scales)
    assert np.isclose(results["x"].sum(), 0, atol=1e-6)
    assert np.isclose(results["y"].sum(), 1, atol=1e-6)

    hist = Hist(stat=stat, common_bins=False, discrete=True)
    results = hist(data, groupby, "x", scales)
    assert np.isclose(results["x"].sum(), 0, atol=1e-6)
    assert np.isclose(results["y"].sum(), 1, atol=1e-6)


def test_hist_frequency():

    x = np.random.normal(size=100)
    y = np.random.normal(size=100)
    data = pd.DataFrame({"x": x, "y": y})
    groupby = GroupBy(["x", "y"])
    scales = {v: Continuous() for v in ["x", "y"]}

    hist = Hist(stat="frequency")
    results = hist(data, groupby, "x", scales)
    assert np.isclose(results["x"].sum(), 0, atol=1e-6)
    assert np.isclose(results["y"].sum(), data.shape[0], atol=1e-6)

    hist = Hist(stat="frequency", discrete=True)
    results = hist(data, groupby, "x", scales)
    assert np.isclose(results["x"].sum(), 0, atol=1e-6)
    assert np.isclose(results["y"].sum(), data.shape[0], atol=1e-6)

    hist = Hist(stat="frequency", common_bins=False)
    results = hist(data, groupby, "x", scales)
    assert np.isclose(results["x"].sum(), 0, atol=1e-6)
    assert np.isclose(results["y"].sum(), data.shape[0], atol=1e-6)

    hist = Hist(stat="frequency", common_bins=False, discrete=True)
    results = hist(data, groupby, "x", scales)
    assert np.isclose(results["x"].sum(), 0, atol=1e-6)
    assert np.isclose(results["y"].sum(), data.shape[0], atol=1e-6)


def test_hist_cumulative():

    x = np.random.normal(size=100)
    y = np.random.normal(size=100)
    data = pd.DataFrame({"x": x, "y": y})
    groupby = GroupBy(["x", "y"])
    scales = {v: Continuous() for v in ["x", "y"]}

    hist = Hist(cumulative=True)
    results = hist(data, groupby, "x", scales)
    assert np.isclose(results["x"].sum(), 0, atol=1e-6)
    assert results["y"].is_monotonic_increasing

    hist = Hist(cumulative=True, discrete=True)
    results = hist(data, groupby, "x", scales)
    assert np.isclose(results["x"].sum(), 0, atol=1e-6)
    assert results["y"].is_monotonic_increasing

    hist = Hist(cumulative=True, common_bins=False)
    results = hist(data, groupby, "x", scales)
    assert np.isclose(results["x"].sum(), 0, atol=1e-6)
    assert results["y"].is_monotonic_increasing

    hist = Hist(cumulative=True, common_bins=False, discrete=True)
    results = hist(data, groupby, "x", scales)
    assert np.isclose(results["x"].sum(), 0, atol=1e-6)
    assert results["y"].is_monotonic_increasing


def test_hist_weight():

    n = 100
    x = np.random.normal(size=n)
    y = np.random.normal(size=n)
    weight = np.random.uniform(size=n)
    data = pd.DataFrame({"x": x, "y": y, "weight": weight})
    groupby = GroupBy(["x", "y"])
    scales = {v: Continuous() for v in ["x", "y"]}

    hist = Hist()
    results = hist(data, groupby, "x", scales)
    assert np.isclose(results["x"].sum(), 0, atol=1e-6)
    assert np.isclose(results["y"].sum(), weight.sum(), atol=1e-6)

    hist = Hist(discrete=True)
    results = hist(data, groupby, "x", scales)
    assert np.isclose(results["x"].sum(), 0, atol=1e-6)
    assert np.isclose(results["y"].sum(), weight.sum(), atol=1e-6)

    hist = Hist(common_bins=False)
    results = hist(data, groupby, "x", scales)
    assert np.isclose(results["x"].sum(), 0, atol=1e-6)
    assert np.isclose(results["y"].sum(), weight.sum(), atol=1e-6)

    hist = Hist(common_bins=False, discrete=True)
    results = hist(data, groupby, "x", scales)
    assert np.isclose(results["x"].sum(), 0, atol=1e-6)
    assert np.isclose(results["y"].sum(), weight.sum(), atol=1e-6)


def test_hist_common_bins():

    n = 100
    x = np.random.normal(size=n)
    y = np.random.normal(size=n)
    b = np.random.choice(["a", "b", "c"], size=n)
    data = pd.DataFrame({"x": x, "y": y, "b": b})
    groupby = GroupBy(["b"])
    scales = {v: Continuous() for v in ["x", "y"]}

    hist = Hist(common_bins=True)
    results = hist(data, groupby, "x", scales)
    assert results["x"].value_counts().max() == results["x"].value_counts().min()

    hist = Hist(common_bins=True, discrete=True)
    results = hist(data, groupby, "x", scales)
    assert results["x"].value_counts().max() == results["x"].value_counts().min()

    groupby = GroupBy(["b", "x", "y"])
    hist = Hist(common_bins=False)
    results = hist(data, groupby, "x", scales)
    assert results["x"].value_counts().max() != results["x"].value_counts().min()

    hist = Hist(common_bins=False, discrete=True)
    results = hist(data, groupby, "x", scales)
    assert results["x"].value_counts().max() != results["x"].value_counts().min()


def test_hist_common_norm():

    n = 100
    x = np.random.normal(size=n)
    y = np.random.normal(size=n)
    b = np.random.choice(["a", "b", "c"], size=n)
    data = pd.DataFrame({"x": x, "y": y, "b": b})
    groupby = GroupBy(["b"])
    scales = {v: Continuous() for v in ["x", "y"]}

    hist = Hist(stat="density", common_norm=True)
    results = hist(data, groupby, "x", scales)
    assert np.isclose(results["x"].sum(), 0, atol=1e-6)
    assert np.isclose(results["y"].sum(), 1, atol=1e-6)

    hist = Hist(stat="density", common_norm=True, discrete=True)
    results = hist(data, groupby, "x", scales)
    assert np.isclose(results["x"].sum(), 0, atol=1e-6)
    assert np.isclose(results["y"].sum(), 1, atol=1e-6)

    groupby = GroupBy(["b", "x", "y"])
    hist = Hist(stat="density", common_norm=False)
    results = hist(data, groupby, "x", scales)
    assert not np.isclose(results["y"].sum(), 1, atol=1e-6)

    hist = Hist(stat="density", common_norm=False, discrete=True)
    results = hist(data, groupby, "x", scales)
    assert not np.isclose(results["y"].sum(), 1, atol=1e-6)


@pytest.mark.parametrize("stat", ["count", "density", "probability"])
@pytest.mark.parametrize("common_bins", [True, False])
@pytest.mark.parametrize("common_norm", [True, False])
@pytest.mark.parametrize("cumulative", [True, False])
@pytest.mark.parametrize("discrete", [True, False])
@pytest.mark.parametrize("orient", ["x", "y"])
@pytest.mark.parametrize("bins", ["auto", "fd", "doane", "scott", "rice", "sturges", "sqrt", 3])
@pytest.mark.parametrize("binrange", [None, (-10, 10)])
@pytest.mark.parametrize("binwidth", [None, 1])
@pytest.mark.parametrize("weight", [False, True])
def test_hist(
    stat, common_bins, common_norm, cumulative, discrete, orient,
    bins, binrange, binwidth, weight,
):

    n = 100
    x = np.random.normal(size=n)
    y = np.random.normal(size=n)
    b = np.random.choice(["a", "b", "c"], size=n)
    data = pd.DataFrame({"x": x, "y": y, "b": b})
    if weight:
        data["weight"] = np.random.uniform(size=n)
    groupby = GroupBy(["b"])
    scales = {v: Continuous() for v in ["x", "y"]}

    hist = Hist(
        stat=stat, common_bins=common_bins, common_norm=common_norm,
        cumulative=cumulative, discrete=discrete,
        bins=bins, binrange=binrange, binwidth=binwidth,
    )
    results = hist(data, groupby, orient, scales)
    assert not results.empty


@pytest.mark.parametrize("stat", ["count", "density", "probability"])
@pytest.mark.parametrize("common_bins", [True, False])
@pytest.mark.parametrize("common_norm", [True, False])
@pytest.mark.parametrize("cumulative", [True, False])
@pytest.mark.parametrize("discrete", [True, False])
@pytest.mark.parametrize("orient", ["x", "y"])
@pytest.mark.parametrize("bins", ["auto", "fd", "doane", "scott", "rice", "sturges", "sqrt", 3])
@pytest.mark.parametrize("binrange", [None, (-10, 10)])
@pytest.mark.parametrize("binwidth", [None, 1])
@pytest.mark.parametrize("weight", [False, True])
@pytest.mark.parametrize("grouping_vars", [("b",), ("b", "c")])
def test_hist_grouping_vars(
    stat, common_bins, common_norm, cumulative, discrete, orient,
    bins, binrange, binwidth, weight, grouping_vars,
):

    n = 100
    x = np.random.normal(size=n)
    y = np.random.normal(size=n)
    b = np.random.choice(["a", "b", "c"], size=n)
    c = np.random.choice(["d", "e", "f"], size=n)
    data = pd.DataFrame({"x": x, "y": y, "b": b, "c": c})
    if weight:
        data["weight"] = np.random.uniform(size=n)
    groupby = GroupBy(grouping_vars)
    scales = {v: Continuous() for v in ["x", "y"]}

    hist = Hist(
        stat=stat, common_bins=common_bins, common_norm=common_norm,
        cumulative=cumulative, discrete=discrete,
        bins=bins, binrange=binrange, binwidth=binwidth,
    )
    results = hist(data, groupby, orient, scales)
    assert not results.empty


@pytest.mark.parametrize("stat", ["count", "density", "probability"])
@pytest.mark.parametrize("common_bins", [True, False])
@pytest.mark.parametrize("common_norm", [True, False])
@pytest.mark.parametrize("cumulative", [True, False])
@pytest.mark.parametrize("discrete", [True, False])
@pytest.mark.parametrize("orient", ["x", "y"])
@pytest.mark.parametrize("bins", ["auto", "fd", "doane", "scott", "rice", "sturges", "sqrt", 3])
@pytest.mark.parametrize("binrange", [None, (-10, 10)])
@pytest.mark.parametrize("binwidth", [None, 1])
@pytest.mark.parametrize("weight", [False, True])
@pytest.mark.parametrize("common_bins_vars", [["b"], ["x", "y"]])
@pytest.mark.parametrize("common_norm_vars", [["b"], ["x", "y"]])
def test_hist_common_vars(
    stat, common_bins, common_norm, cumulative, discrete, orient,
    bins, binrange, binwidth, weight, common_bins_vars, common_norm_vars,
):

    n = 100
    x = np.random.normal(size=n)
    y = np.random.normal(size=n)
    b = np.random.choice(["a", "b", "c"], size=n)
    data = pd.DataFrame({"x": x, "y": y, "b": b})
    if weight:
        data["weight"] = np.random.uniform(size=n)
    groupby = GroupBy(["b"])
    scales = {v: Continuous() for v in ["x", "y"]}

    hist = Hist(
        stat=stat, common_bins=common_bins_vars, common_norm=common_norm_vars,
        cumulative=cumulative, discrete=discrete,
        bins=bins, binrange=binrange, binwidth=binwidth,
    )
    results = hist(data, groupby, orient, scales)
    assert not results.empty


@pytest.mark.parametrize("common_bins_vars", [["b"], ["x", "y"]])
@pytest.mark.parametrize("common_norm_vars", [["b"], ["x", "y"]])
def test_hist_common_vars_warning(common_bins_vars, common_norm_vars):

    n = 100
    x = np.random.normal(size=n)
    y = np.random.normal(size=n)
    b = np.random.choice(["a", "b", "c"], size=n)
    data = pd.DataFrame({"x": x, "y": y, "b": b})
    groupby = GroupBy(["b"])
    scales = {v: Continuous() for v in ["x", "y"]}

    with pytest.warns(UserWarning, match="Undefined variable"):
        hist = Hist(common_bins=common_bins_vars, common_norm=common_norm_vars)
        hist(data, groupby, "x", scales)


@pytest.mark.parametrize("stat", ["count", "density", "probability"])
@pytest.mark.parametrize("common_bins", [True, False])
@pytest.mark.parametrize("common_norm", [True, False])
@pytest.mark.parametrize("cumulative", [True, False])
@pytest.mark.parametrize("discrete", [True, False])
@pytest.mark.parametrize("orient", ["x", "y"])
@pytest.mark.parametrize("bins", ["auto", "fd", "doane", "scott", "rice", "sturges", "sqrt", 3])
@pytest.mark.parametrize("binrange", [None, (-10, 10)])
@pytest.mark.parametrize("binwidth", [None, 1])
@pytest.mark.parametrize("weight", [False, True])
def test_hist_empty(
    stat, common_bins, common_norm, cumulative, discrete, orient,
    bins, binrange, binwidth, weight,
):

    x = np.random.normal(size=0)
    y = np.random.normal(size=0)
    b = np.random.choice(["a", "b", "c"], size=0)
    data = pd.DataFrame({"x": x, "y": y, "b": b})
    if weight:
        data["weight"] = np.random.uniform(size=0)
    groupby = GroupBy(["b"])
    scales = {v: Continuous() for v in ["x", "y"]}

    hist = Hist(
        stat=stat, common_bins=common_bins, common_norm=common_norm,
        cumulative=cumulative, discrete=discrete,
        bins=bins, binrange=binrange, binwidth=binwidth,
    )
    results = hist(data, groupby, orient, scales)
    assert results.empty


@pytest.mark.parametrize("stat", ["count", "density", "probability"])
@pytest.mark.parametrize("common_bins", [True, False])
@pytest.mark.parametrize("common_norm", [True, False])
@pytest.mark.parametrize("cumulative", [True, False])
@pytest.mark.parametrize("discrete", [True, False])
@pytest.mark.parametrize("orient", ["x", "y"])
@pytest.mark.parametrize("bins", ["auto", "fd", "doane", "scott", "rice", "sturges", "sqrt", 3])
@pytest.mark.parametrize("binrange", [None, (-10, 10)])
@pytest.mark.parametrize("binwidth", [None, 1])
@pytest.mark.parametrize("weight", [False, True])
def test_hist_invalid(
    stat, common_bins, common_norm, cumulative, discrete, orient,
    bins, binrange, binwidth, weight,
):

    x = np.random.normal(size=100)
    y = np.random.normal(size=100)
    b = np.random.choice(["a", "b", "c"], size=100)
    data = pd.DataFrame({"x": x, "y": y, "b": b})
    if weight:
        data["weight"] = np.random.uniform(size=100)
    groupby = GroupBy(["b"])
    scales = {v: Continuous() for v in ["x", "y"]}

    hist = Hist(
        stat=stat, common_bins=common_bins, common_norm=common_norm,
        cumulative=cumulative, discrete=discrete,
        bins=bins, binrange=binrange, binwidth=binwidth,
    )
    results = hist(data, groupby, orient, scales)
    assert not results.empty


@pytest.mark.parametrize("stat", ["count", "density", "probability"])
@pytest.mark.parametrize("common_bins", [True, False])
@pytest.mark.parametrize("common_norm", [True, False])
@pytest.mark.parametrize("cumulative", [True, False])
@pytest.mark.parametrize("discrete", [True, False])
@pytest.mark.parametrize("orient", ["x", "y"])
@pytest.mark.parametrize("bins", ["auto", "fd", "doane", "scott", "rice", "sturges", "sqrt", 3])
@pytest.mark.parametrize("binrange", [None, (-10, 10)])
@pytest.mark.parametrize("binwidth", [None, 1])
@pytest.mark.parametrize("weight", [False, True])
def test_hist_nan(
    stat, common_bins, common_norm, cumulative, discrete, orient,
    bins, binrange, binwidth, weight,
):

    x = np.random.normal(size=100)
    y = np.random.normal(size=100)
    b = np.random.choice(["a", "b", "c"], size=100)
    data = pd.DataFrame({"x": x, "y": y, "b": b})
    if weight:
        data["weight"] = np.random.uniform(size=100)
    groupby = GroupBy(["b"])
    scales = {v: Continuous() for v in ["x", "y"]}

    data.loc[0, "x"] = np.nan
    data.loc[1, "y"] = np.nan
    if weight:
        data.loc[2, "weight"] = np.nan

    hist = Hist(
        stat=stat, common_bins=common_bins, common_norm=common_norm,
        cumulative=cumulative, discrete=discrete,
        bins=bins, binrange=binrange, binwidth=binwidth,
    )
    results = hist(data, groupby, orient, scales)
    assert not results.empty


@pytest.mark.parametrize("stat", ["count", "density", "probability"])
@pytest.mark.parametrize("common_bins", [True, False])
@pytest.mark.parametrize("common_norm", [True, False])
@pytest.mark.parametrize("cumulative", [True, False])
@pytest.mark.parametrize("discrete", [True, False])
@pytest.mark.parametrize("orient", ["x", "y"])
@pytest.mark.parametrize("bins", ["auto", "fd", "doane", "scott", "rice", "sturges", "sqrt", 3])
@pytest.mark.parametrize("binrange", [None, (-10, 10)])
@pytest.mark.parametrize("binwidth", [None, 1])
@pytest.mark.parametrize("weight", [False, True])
@pytest.mark.parametrize("grouping_vars", [("b",), ("b", "c")])
def test_hist_grouping_vars_nan(
    stat, common_bins, common_norm, cumulative, discrete, orient,
    bins, binrange, binwidth, weight, grouping_vars,
):

    x = np.random.normal(size=100)
    y = np.random.normal(size=100)
    b = np.random.choice(["a", "b", "c"], size=100)
    c = np.random.choice(["d", "e", "f"], size=100)
    data = pd.DataFrame({"x": x, "y": y, "b": b, "c": c})
    if weight:
        data["weight"] = np.random.uniform(size=100)
    groupby = GroupBy(grouping_vars)
    scales = {v: Continuous() for v in ["x", "y"]}

    data.loc[0, "x"] = np.nan
    data.loc[1, "y"] = np.nan
    data.loc[2, "b"] = np.nan
    data.loc[3, "c"] = np.nan
    if weight:
        data.loc[4, "weight"] = np.nan

    hist = Hist(
        stat=stat, common_bins=common_bins, common_norm=common_norm,
        cumulative=cumulative, discrete=discrete,
        bins=bins, binrange=binrange, binwidth=binwidth,
    )
    results = hist(data, groupby, orient, scales)
    assert not results.empty


@pytest.mark.parametrize("stat", ["count", "density", "probability"])
@pytest.mark.parametrize("common_bins", [True, False])
@pytest.mark.parametrize("common_norm", [True, False])
@pytest.mark.parametrize("cumulative", [True, False])
@pytest.mark.parametrize("discrete", [True, False])
@pytest.mark.parametrize("orient", ["x", "y"])
@pytest.mark.parametrize("bins", ["auto", "fd", "doane", "scott", "rice", "sturges", "sqrt", 3])
@pytest.mark.parametrize("binrange", [None, (-10, 10)])
@pytest.mark.parametrize("binwidth", [None, 1])
@pytest.mark.parametrize("weight", [False, True])
@pytest.mark.parametrize("common_bins_vars", [["b"], ["x", "y"]])
@pytest.mark.parametrize("common_norm_vars", [["b"], ["x", "y"]])
def test_hist_common_vars_nan(
    stat, common_bins, common_norm, cumulative, discrete, orient,
    bins, binrange, binwidth, weight, common_bins_vars, common_norm_vars,
):

    x = np.random.normal(size=100)
    y = np.random.normal(size=100)
    b = np.random.choice(["a", "b", "c"], size=100)
    data = pd.DataFrame({"x": x, "y": y, "b": b})
    if weight:
        data["weight"] = np.random.uniform(size=100)
    groupby = GroupBy(["b"])
    scales = {v: Continuous() for v in ["x", "y"]}

    data.loc[0, "x"] = np.nan
    data.loc[1, "y"] = np.nan
    data.loc[2, "b"] = np.nan
    if weight:
        data.loc[3, "weight"] = np.nan

    hist = Hist(
        stat=stat, common_bins=common_bins_vars, common_norm=common_norm_vars,
        cumulative=cumulative, discrete=discrete,
        bins=bins, binrange=binrange, binwidth=binwidth,
    )
    results = hist(data, groupby, orient, scales)
    assert not results.empty


@pytest.mark.parametrize("stat", ["count", "density", "probability"])
@pytest.mark.parametrize("common_bins", [True, False])
@pytest.mark.parametrize("common_norm", [True, False])
@pytest.mark.parametrize("cumulative", [True, False])
@pytest.mark.parametrize("discrete", [True, False])
@pytest.mark.parametrize("orient", ["x", "y"])
@pytest.mark.parametrize("bins", ["auto", "fd", "doane", "scott", "rice", "sturges", "sqrt", 3])
@pytest.mark.parametrize("binrange", [None, (-10, 10)])
@pytest.mark.parametrize("binwidth", [None, 1])
@pytest.mark.parametrize("weight", [False, True])
@pytest.mark.parametrize("grouping_vars", [("b",), ("b", "c")])
def test_hist_grouping_vars_nan(
    stat, common_bins, common_norm, cumulative, discrete, orient,
    bins, binrange, binwidth, weight, grouping_vars,
):

    x = np.random.normal(size=100)
    y = np.random.normal(size=100)
    b = np.random.choice(["a", "b", "c"], size=100)
    c = np.random.choice(["d", "e", "f"], size=100)
    data = pd.DataFrame({"x": x, "y": y, "b": b, "c": c})
    if weight:
        data["weight"] = np.random.uniform(size=100)
    groupby = GroupBy(grouping_vars)
    scales = {v: Continuous() for v in ["x", "y"]}

    data.loc[0, "x"] = np.nan
    data.loc[1, "y"] = np.nan
    data.loc[2, "b"] = np.nan
    data.loc[3, "c"] = np.nan
    if weight:
        data.loc[4, "weight"] = np.nan

    hist = Hist(
        stat=stat, common_bins=common_bins, common_norm=common_norm,
        cumulative=cumulative, discrete=discrete,
        bins=bins, binrange=binrange, binwidth=binwidth,
    )
    results = hist(data, groupby, orient, scales)
    assert not results.empty


@pytest.mark.parametrize("stat", ["count", "density", "probability"])
@pytest.mark.parametrize("common_bins", [True, False])
@pytest.mark.parametrize("common_norm", [True, False])
@pytest.mark.parametrize("cumulative", [True, False])
@pytest.mark.parametrize("discrete", [True, False])
@pytest.mark.parametrize("orient", ["x", "y"])
@pytest.mark.parametrize("bins", ["auto", "fd", "doane", "scott", "rice", "sturges", "sqrt", 3])
@pytest.mark.parametrize("binrange", [None, (-10, 10)])
@pytest.mark.parametrize("binwidth", [None, 1])
@pytest.mark.parametrize("weight", [False, True])
@pytest.mark.parametrize("common_bins_vars", [["b"], ["x", "y"]])
@pytest.mark.parametrize("common_norm_vars", [["b"], ["x", "y"]])
def test_hist_common_vars_nan(
    stat, common_bins, common_norm, cumulative, discrete, orient,
    bins, binrange, binwidth, weight, common_bins_vars, common_norm_vars,
):

    x = np.random.normal(size=100)
    y = np.random.normal(size=100)
    b = np.random.choice(["a", "b", "c"], size=100)
    data = pd.DataFrame({"x": x, "y": y, "b": b})
    if weight:
        data["weight"] = np.random.uniform(size=100)
    groupby = GroupBy(["b"])
    scales = {v: Continuous() for v in ["x", "y"]}

    data.loc[0, "x"] = np.nan
    data.loc[1, "y"] = np.nan
    data.loc[2, "b"] = np.nan
    if weight:
        data.loc[3, "weight"] = np.nan

    hist = Hist(
        stat=stat, common_bins=common_bins_vars, common_norm=common_norm_vars,
        cumulative=cumulative, discrete=discrete,
        bins=bins, binrange=binrange, binwidth=binwidth,
    )
    results = hist(data, groupby, orient, scales)
    assert not results.empty


@pytest.mark.parametrize("stat", ["count", "density", "probability"])
@pytest.mark.parametrize("common_bins", [True, False])
@pytest.mark.parametrize("common_norm", [True, False])
@pytest.mark.parametrize("cumulative", [True, False])
@pytest.mark.parametrize("discrete", [True, False])
@pytest.mark.parametrize("orient", ["x", "y"])
@pytest.mark.parametrize("bins", ["auto", "fd", "doane", "scott", "rice", "sturges", "sqrt", 3])
@pytest.mark.parametrize("binrange", [None, (-10, 10)])
@pytest.mark.parametrize("binwidth", [None, 1])
@pytest.mark.parametrize("weight", [False, True])
@pytest.mark.parametrize("common_bins_vars", [["b"], ["x", "y"]])
@pytest.mark.parametrize("common_norm_vars", [["b"], ["x", "y"]])
def test_hist_common_vars(
    stat, common_bins, common_norm, cumulative, discrete, orient,
    bins, binrange, binwidth, weight, common_bins_vars, common_norm_vars,
):

    n = 100
    x = np.random.normal(size=n)
    y = np.random.normal(size=n)
    b = np.random.choice(["a", "b", "c"], size=n)
    data = pd.DataFrame({"x": x, "y": y, "b": b})
    if weight:
        data["weight"] = np.random.uniform(size=n)
    groupby = GroupBy(["b"])
    scales = {v: Continuous() for v in ["x", "y"]}

    hist = Hist(
        stat=stat, common_bins=common_bins_vars, common_norm=common_norm_vars,
        cumulative=cumulative, discrete=discrete,
        bins=bins, binrange=binrange, binwidth=binwidth,
    )
    results = hist(data, groupby, orient, scales)
    assert not results.empty


@pytest.mark.parametrize("common_bins_vars", [["b"], ["x", "y"]])
@pytest.mark.parametrize("common_norm_vars", [["b"], ["x", "y"]])
def test_hist_common_vars_warning(common_bins_vars, common_norm_vars):

    n = 100
    x = np.random.normal(size=n)
    y = np.random.normal(size=n)
    b = np.random.choice(["a", "b", "c"], size=n)
    data = pd.DataFrame({"x": x, "y": y, "b": b})
    groupby = GroupBy(["b"])
    scales = {v: Continuous() for v in ["x", "y"]}

    with pytest.warns(UserWarning, match="Undefined variable"):
        hist = Hist(common_bins=common_bins_vars, common_norm=common_norm_vars)
        hist(data, groupby, "x", scales)


@pytest.mark.parametrize("stat", ["count", "density", "probability"])
@pytest.mark.parametrize("common_bins", [True, False])
@pytest.mark.parametrize("common_norm", [True, False])
@pytest.mark.parametrize("cumulative", [True, False])
@pytest.mark.parametrize("discrete", [True, False])
@pytest.mark.parametrize("orient", ["x", "y"])
@pytest.mark.parametrize("bins", ["auto", "fd", "doane", "scott", "rice", "sturges", "sqrt", 3])
@pytest.mark.parametrize("binrange", [None, (-10, 10)])
@pytest.mark.parametrize("binwidth", [None, 1])
@pytest.mark.parametrize("weight", [False, True])
def test_hist_empty(
    stat, common_bins, common_norm, cumulative, discrete, orient,
    bins, binrange, binwidth, weight,
):

    x = np.random.normal(size=0)
    y = np.random.normal(size=0)
    b = np.random.choice(["a", "b", "c"], size=0)
    data = pd.DataFrame({"x": x, "y": y, "b": b})
    if weight:
        data["weight"] = np.random.uniform(size=0)
    groupby = GroupBy(["b"])
    scales = {v: Continuous() for v in ["x", "y"]}

    hist = Hist(
        stat=stat, common_bins=common_bins, common_norm=common_norm,
        cumulative=cumulative, discrete=discrete,
        bins=bins, binrange=binrange, binwidth=binwidth,
    )
    results = hist(data, groupby, orient, scales)
    assert results.empty


@pytest.mark.parametrize("stat", ["count", "density", "probability"])
@pytest.mark.parametrize("common_bins", [True, False])
@pytest.mark.parametrize("common_norm", [True, False])
@pytest.mark.parametrize("cumulative", [True, False])
@pytest.mark.parametrize("discrete", [True, False])
@pytest.mark.parametrize("orient", ["x", "y"])
@pytest.mark.parametrize("bins", ["auto", "fd", "doane", "scott", "rice", "sturges", "sqrt", 3])
@pytest.mark.parametrize("binrange", [None, (-10, 10)])
@pytest.mark.parametrize("binwidth", [None, 1])
@pytest.mark.parametrize("weight", [False, True])
def test_hist_invalid(
    stat, common_bins, common_norm, cumulative, discrete, orient,
    bins, binrange, binwidth, weight,
):

    x = np.random.normal(size=100)
    y = np.random.normal(size=100)
    b = np.random.choice(["a", "b", "c"], size=100)
    data = pd.DataFrame({"x": x, "y": y, "b": b})
    if weight:
        data["weight"] = np.random.uniform(size=100)
    groupby = GroupBy(["b"])
    scales = {v: Continuous() for v in ["x", "y"]}

    hist = Hist(
        stat=stat, common_bins=common_bins, common_norm=common_norm,
        cumulative=cumulative, discrete=discrete,
        bins=bins, binrange=binrange, binwidth=binwidth,
    )
    results = hist(data, groupby, orient, scales)
    assert not results.empty


@pytest.mark.parametrize("stat", ["count", "density", "probability"])
@pytest.mark.parametrize("common_bins", [True, False])
@pytest.mark.parametrize("common_norm", [True, False])
@pytest.mark.parametrize("cumulative", [True, False])
@pytest.mark.parametrize("discrete", [True, False])
@pytest.mark.parametrize("orient", ["x", "y"])
@pytest.mark.parametrize("bins", ["auto", "fd", "doane", "scott", "rice", "sturges", "sqrt", 3])
@pytest.mark.parametrize("binrange", [None, (-10, 10)])
@pytest.mark.parametrize("binwidth", [None, 1])
@pytest.mark.parametrize("weight", [False, True])
def test_hist_nan(
    stat, common_bins, common_norm, cumulative, discrete, orient,
    bins, binrange, binwidth, weight,
):

    x = np.random.normal(size=100)
    y = np.random.normal(size=100)
    b = np.random.choice(["a", "b", "c"], size=100)
    data = pd.DataFrame({"x": x, "y": y, "b": b})
    if weight:
        data["weight"] = np.random.uniform(size=100)
    groupby = GroupBy(["b"])
    scales = {v: Continuous() for v in ["x", "y"]}

    data.loc[0, "x"] = np.nan
    data.loc[1, "y"] = np.nan
    if weight:
        data.loc[2, "weight"] = np.nan

    hist = Hist(
        stat=stat, common_bins=common_bins, common_norm=common_norm,
        cumulative=cumulative, discrete=discrete,
        bins=bins, binrange=binrange, binwidth=binwidth,
    )
    results = hist(data, groupby, orient, scales)
    assert not results.empty


@pytest.mark.parametrize("stat", ["count", "density", "probability"])
@pytest.mark.parametrize("common_bins", [True, False])
@pytest.mark.parametrize("common_norm", [True, False])
@pytest.mark.parametrize("cumulative", [True, False])
@pytest.mark.parametrize("discrete", [True, False])
@pytest.mark.parametrize("orient", ["x", "y"])
@pytest.mark.parametrize("bins", ["auto", "fd", "doane", "scott", "rice", "sturges", "sqrt", 3])
@pytest.mark.parametrize("binrange", [None, (-10, 10)])
@pytest.mark.parametrize("binwidth", [None, 1])
@pytest.mark.parametrize("weight", [False, True])
@pytest.mark.parametrize("grouping_vars", [("b",), ("b", "c")])
def test_hist_grouping_vars_nan(
    stat, common_bins, common_norm, cumulative, discrete, orient,
    bins, binrange, binwidth, weight, grouping_vars,
):

    x = np.random.normal(size=100)
    y = np.random.normal(size=100)
    b = np.random.choice(["a", "b", "c"], size=100)
    c = np.random.choice(["d", "e", "f"], size=100)
    data = pd.DataFrame({"x": x, "y": y, "b": b, "c": c})
    if weight:
        data["weight"] = np.random.uniform(size=100)
    groupby = GroupBy(grouping_vars)
    scales = {v: Continuous() for v in ["x", "y"]}

    data.loc[0, "x"] = np.nan
    data.loc[1, "y"] = np.nan
    data.loc[2, "b"] = np.nan
    data.loc[3, "c"] = np.nan
    if weight:
        data.loc[4, "weight"] = np.nan

    hist = Hist(
        stat=stat, common_bins=common_bins, common_norm=common_norm,
        cumulative=cumulative, discrete=discrete,
        bins=bins, binrange=binrange, binwidth=binwidth,
    )
    results = hist(data, groupby, orient, scales)
    assert not results.empty


@pytest.mark.parametrize("stat", ["count", "density", "probability"])
@pytest.mark.parametrize("common_bins", [True, False])
@pytest.mark.parametrize("common_norm", [True, False])
@pytest.mark.parametrize("cumulative", [True, False])
@pytest.mark.parametrize("discrete", [True, False])
@pytest.mark.parametrize("orient", ["x", "y"])
@pytest.mark.parametrize("bins", ["auto", "fd", "doane", "scott", "rice", "sturges", "sqrt", 3])
@pytest.mark.parametrize("binrange", [None, (-10, 10)])
@pytest.mark.parametrize("binwidth", [None, 1])
@pytest.mark.parametrize("weight", [False, True])
@pytest.mark.parametrize("common_bins_vars", [["b"], ["x", "y"]])
@pytest.mark.parametrize("common_norm_vars", [["b"], ["x", "y"]])
def test_hist_common_vars_nan(
    stat, common_bins, common_norm, cumulative, discrete, orient,
    bins, binrange, binwidth, weight, common_bins_vars, common_norm_vars,
):

    x = np.random.normal(size=100)
    y = np.random.normal(size=100)
    b = np.random.choice(["a", "b", "c"], size=100)
    data = pd.DataFrame({"x": x, "y": y, "b": b})
    if weight:
        data["weight"] = np.random.uniform(size=100)
    groupby = GroupBy(["b"])
    scales = {v: Continuous() for v in ["x", "y"]}

    data.loc[0, "x"] = np.nan
    data.loc[1, "y"] = np.nan
    data.loc[2, "b"] = np.nan
    if weight:
        data.loc[3, "weight"] = np.nan

    hist = Hist(
        stat=stat, common_bins=common_bins_vars, common_norm=common_norm_vars,
        cumulative=cumulative, discrete=discrete,
        bins=bins, binrange=binrange, binwidth=binwidth,
    )
    results = hist(data, groupby, orient, scales)
    assert not results.empty


@pytest.mark.parametrize("stat", ["count", "density", "probability"])
@pytest.mark.parametrize("common_bins", [True, False])
@pytest.mark.parametrize("common_norm", [True, False])
@pytest.mark.parametrize("cumulative", [True, False])
@pytest.mark.parametrize("discrete", [True, False])
@pytest.mark.parametrize("orient", ["x", "y"])
@pytest.mark.parametrize("bins", ["auto", "fd", "doane", "scott", "rice", "sturges", "sqrt", 3])
@pytest.mark.parametrize("binrange", [None, (-10, 10)])
@pytest.mark.parametrize("binwidth", [None, 1])
@pytest.mark.parametrize("weight", [False, True])
@pytest.mark.parametrize("grouping_vars", [("b",), ("b", "c")])
def test_hist_grouping_vars_nan(
    stat, common_bins, common_norm, cumulative, discrete, orient,
    bins, binrange, binwidth, weight, grouping_vars,
):

    x = np.random.normal(size=100)
    y = np.random.normal(size=100)
    b = np.random.choice(["a", "b", "c"], size=100)
    c = np.random.choice(["d", "e", "f"], size=100)
    data = pd.DataFrame({"x": x, "y": y, "b": b, "c": c})
    if weight:
        data["weight"] = np.random.uniform(size=100)
    groupby = GroupBy(grouping_vars)
    scales = {v: Continuous() for v in ["x", "y"]}

    data.loc[0, "x"] = np.nan
    data.loc[1, "y"] = np.nan
    data.loc[2, "b"] = np.nan
    data.loc[3, "c"] = np.nan
    if weight:
        data.loc[4, "weight"] = np.nan

    hist = Hist(
        stat=stat, common_bins=common_bins, common_norm=common_norm,
        cumulative=cumulative, discrete=discrete,
        bins=bins, binrange=binrange, binwidth=binwidth,
    )
    results = hist(data, groupby, orient, scales)
    assert not results.empty


@pytest.mark.parametrize("stat", ["count", "density", "probability"])
@pytest.mark.parametrize("common_bins", [True, False])
@pytest.mark.parametrize("common_norm", [True, False])
@pytest.mark.parametrize("cumulative", [True, False])
@pytest.mark.parametrize("discrete", [True, False])
@pytest.mark.parametrize("orient", ["x", "y"])
@pytest.mark.parametrize("bins", ["auto", "fd", "doane", "scott", "rice", "sturges", "sqrt", 3])
@pytest.mark.parametrize("binrange", [None, (-10, 10)])
@pytest.mark.parametrize("binwidth", [None, 1])
@pytest.mark.parametrize("weight", [False, True])
@pytest.mark.parametrize("common_bins_vars", [["b"], ["x", "y"]])
@pytest.mark.parametrize("common_norm_vars", [["b"], ["x", "y"]])
def test_hist_common_vars_nan(
    stat, common_bins, common_norm, cumulative, discrete, orient,
    bins, binrange, binwidth, weight, common_bins_vars, common_norm_vars,
):

    x = np.random.normal(size=100)
    y = np.random.normal(size=100)
    b = np.random.choice(["a", "b", "c"], size=100)
    data = pd.DataFrame({"x": x, "y": y, "b": b})
    if weight:
        data["weight"] = np.random.uniform(size=100)
    groupby = GroupBy(["b"])
    scales = {v: Continuous() for v in ["x", "y"]}

    data.loc[0, "x"] = np.nan
    data.loc[1, "y"] = np.nan
    data.loc[2, "b"] = np.nan
    if weight:
        data.loc[3, "weight"] = np.nan

    hist = Hist(
        stat=stat, common_bins=common_bins_vars, common_norm=common_norm_vars,
        cumulative=cumulative, discrete=discrete,
        bins=bins, binrange=binrange, binwidth=binwidth,
    )
    results = hist(data, groupby, orient, scales)
    assert not results.empty


@pytest.mark.parametrize("stat", ["count", "density", "probability"])
@pytest.mark.parametrize("common_bins", [True, False])
@pytest.mark.parametrize("common_norm", [True, False])
@pytest.mark.parametrize("cumulative", [True, False])
@pytest.mark.parametrize("discrete", [True, False])
@pytest.mark.parametrize("orient", ["x", "y"])
@pytest.mark.parametrize("bins", ["auto", "fd", "doane", "scott", "rice", "sturges", "sqrt", 3])
@pytest.mark.parametrize("binrange", [None, (-10, 10)])
@pytest.mark.parametrize("binwidth", [None, 1])
@pytest.mark.parametrize("weight", [False, True])
@pytest.mark.parametrize("common_bins_vars", [["b"], ["x", "y"]])
@pytest.mark.parametrize("common_norm_vars", [["b"], ["x", "y"]])
def test_hist_common_vars(
    stat, common_bins, common_norm, cumulative, discrete, orient,
    bins, binrange, binwidth, weight, common_bins_vars, common_norm_vars,
):

    n = 100
    x = np.random.normal(size=n)
    y = np.random.normal(size=n)
    b = np.random.choice(["a", "b", "c"], size=n)
    data = pd.DataFrame({"x": x, "y": y, "b": b})
    if weight:
        data["weight"] = np.random.uniform(size=n)
    groupby = GroupBy(["b"])
    scales = {v: Continuous() for v in ["x", "y"]}

    hist = Hist(
        stat=stat, common_bins=common_bins_vars, common_norm=common_norm_vars,
        cumulative=cumulative, discrete=discrete,
        bins=bins, binrange=binrange, binwidth=binwidth,
    )
    results = hist(data, groupby, orient, scales)
    assert not results.empty


@pytest.mark.parametrize("common_bins_vars", [["b"], ["x", "y"]])
@pytest.mark.parametrize("common_norm_vars", [["b"], ["x", "y"]])
def test_hist_common_vars_warning(common_bins_vars, common_norm_vars):

    n = 100
    x = np.random.normal(size=n)
    y = np.random.normal(size=n)
    b = np.random.choice(["a", "b", "c"], size=n)
    data = pd.DataFrame({"x": x, "y": y, "b": b})
    groupby = GroupBy(["b"])
    scales = {v: Continuous() for v in ["x", "y"]}

    with pytest.warns(UserWarning, match="Undefined variable"):
        hist = Hist(common_bins=common_bins_vars, common_norm=common_norm_vars)
        hist(data, groupby, "x", scales)


@pytest.mark.parametrize("stat", ["count", "density", "probability"])
@pytest.mark.parametrize("common_bins", [True, False])
@pytest.mark.parametrize("common_norm", [True, False])
@pytest.mark.parametrize("cumulative", [True, False])
@pytest.mark.parametrize("discrete", [True, False])
@pytest.mark.parametrize("orient", ["x", "y"])
@pytest.mark.parametrize("bins", ["auto", "fd", "doane", "scott", "rice", "sturges", "sqrt", 3])
@pytest.mark.parametrize("binrange", [None, (-10, 10)])
@pytest.mark.parametrize("binwidth", [None, 1])
@pytest.mark.parametrize("weight", [False, True])
def test_hist_empty(
    stat, common_bins, common_norm, cumulative, discrete, orient,
    bins, binrange, binwidth, weight,
):

    x = np.random.normal(size=0)
    y = np.random.normal(size=0)
    b = np.random.choice(["a", "b", "c"], size=0)
    data = pd.DataFrame({"x": x, "y": y, "b": b})
    if weight:
        data["weight"] = np.random.uniform(size=0)
    groupby = GroupBy(["b"])
    scales = {v: Continuous() for v in ["x", "y"]}

    hist = Hist(
        stat=stat, common_bins=common_bins, common_norm=common_norm,
        cumulative=cumulative, discrete=discrete,
        bins=bins, binrange=binrange, binwidth=binwidth,
    )
    results = hist(data, groupby, orient, scales)
    assert results.empty


@pytest.mark.parametrize("stat", ["count", "density", "probability"])
@pytest.mark.parametrize("common_bins", [True, False])
@pytest.mark.parametrize("common_norm", [True, False])
@pytest.mark.parametrize("cumulative", [True, False])
@pytest.mark.parametrize("discrete", [True, False])
@pytest.mark.parametrize("orient", ["x", "y"])
@pytest.mark.parametrize("bins", ["auto", "fd", "doane", "scott", "rice", "sturges", "sqrt", 3])
@pytest.mark.parametrize("binrange", [None, (-10, 10)])
@pytest.mark.parametrize("binwidth", [None, 1])
@pytest.mark.parametrize("weight", [False, True])
def test_hist_invalid(
    stat, common_bins, common_norm, cumulative, discrete, orient,
    bins, binrange, binwidth, weight,
):

    x = np.random.normal(size=100)
    y = np.random.normal(size=100)
    b = np.random.choice(["a", "b", "c"], size=100)
    data = pd.DataFrame({"x": x, "y": y, "b": b})
    if weight:
        data["weight"] = np.random.uniform(size=100)
    groupby = GroupBy(["b"])
    scales = {v: Continuous() for v in ["x", "y"]}

    hist = Hist(
        stat=stat, common_bins=common_bins, common_norm=common_norm,
        cumulative=cumulative, discrete=discrete,
        bins=bins, binrange=binrange, binwidth=binwidth,
    )
    results = hist(data, groupby, orient, scales)
    assert not results.empty


@pytest.mark.parametrize("stat", ["count", "density", "probability"])
@pytest.mark.parametrize("common_bins", [True, False])
@pytest.mark.parametrize("common_norm", [True, False])
@pytest.mark.parametrize("cumulative", [True, False])
@pytest.mark.parametrize("discrete", [True, False])
@pytest.mark.parametrize("orient", ["x", "y"])
@pytest.mark.parametrize("bins", ["auto", "fd", "doane", "scott", "rice", "sturges", "sqrt", 3])
@pytest.mark.parametrize("binrange", [None, (-10, 10)])
@pytest.mark.parametrize("binwidth", [None, 1])
@pytest.mark.parametrize("weight", [False, True])
def test_hist_nan(
    stat, common_bins, common_norm, cumulative, discrete, orient,
    bins, binrange, binwidth, weight,
):

    x = np.random.normal(size=100)
    y = np.random.normal(size=100)
    b = np.random.choice(["a", "b", "c"], size=100)
    data = pd.DataFrame({"x": x, "y": y, "b": b})
    if weight:
        data["weight"] = np.random.uniform(size=100)
    groupby = GroupBy(["b"])
    scales = {v: Continuous() for v in ["x", "y"]}

    data.loc[0, "x"] = np.nan
    data.loc[1, "y"] = np.nan
    if weight:
        data.loc[2, "weight"] = np.nan

    hist = Hist(
        stat=stat, common_bins=common_bins, common_norm=common_norm,
        cumulative=cumulative, discrete=discrete,
        bins=bins, binrange=binrange, binwidth=binwidth,
    )
    results = hist(data, groupby, orient, scales)
    assert not results.empty


@pytest.mark.parametrize("stat", ["count", "density", "probability"])
@pytest.mark.parametrize("common_bins", [True, False])
@pytest.mark.parametrize("common_norm", [True, False])
@pytest.mark.parametrize("cumulative", [True, False])
@pytest.mark.parametrize("discrete", [True, False])
@pytest.mark.parametrize("orient", ["x", "y"])
@pytest.mark.parametrize("bins", ["auto", "fd", "doane", "scott", "rice", "sturges", "sqrt", 3])
@pytest.mark.parametrize("binrange", [None, (-10, 10)])
@pytest.mark.parametrize("binwidth", [None, 1])
@pytest.mark.parametrize("weight", [False, True])
@pytest.mark.parametrize("grouping_vars", [("b",), ("b", "c")])
def test_hist_grouping_vars_nan(
    stat, common_bins, common_norm, cumulative, discrete, orient,
    bins, binrange, binwidth, weight, grouping_vars,
):

    x = np.random.normal(size=100)
    y = np.random.normal(size=100)
    b = np.random.choice(["a", "b", "c"], size=100)
    c = np.random.choice(["d", "e", "f"], size=100)
    data = pd.DataFrame({"x": x, "y": y, "b": b, "c": c})
    if weight:
        data["weight"] = np.random.uniform(size=100)
    groupby = GroupBy(grouping_vars)
    scales = {v: Continuous() for v in ["x", "y"]}

    data.loc[0, "x"] = np.nan
    data.loc[1, "y"] = np.nan
    data.loc[2, "b"] = np.nan
    data.loc[3, "c"] = np.nan
    if weight:
        data.loc[4, "weight"] = np.nan

    hist = Hist(
        stat=stat, common_bins=common_bins, common_norm=common_norm,
        cumulative=cumulative, discrete=discrete,
        bins=bins, binrange=binrange, binwidth=binwidth,
    )
    results = hist(data, groupby, orient, scales)
    assert not results.empty


@pytest.mark.parametrize("stat", ["count", "density", "probability"])
@pytest.mark.parametrize("common_bins", [True, False])
@pytest.mark.parametrize("common_norm", [True, False])
@pytest.mark.parametrize("cumulative", [True, False])
@pytest.mark.parametrize("discrete", [True, False])
@pytest.mark.parametrize("orient", ["x", "y"])
@pytest.mark.parametrize("bins", ["auto", "fd", "doane", "scott", "rice", "sturges", "sqrt", 3])
@pytest.mark.parametrize("binrange", [None, (-10, 10)])
@pytest.mark.parametrize("binwidth", [None, 1])
@pytest.mark.parametrize("weight", [False, True])
@pytest.mark.parametrize("common_bins_vars", [["b"], ["x", "y"]])
@pytest.mark.parametrize("common_norm_vars", [["b"], ["x", "y"]])
def test_hist_common_vars_nan(
    stat, common_bins, common_norm, cumulative, discrete, orient,
    bins, binrange, binwidth, weight, common_bins_vars, common_norm_vars,
):

    x = np.random.normal(size=100)
    y = np.random.normal(size=100)
    b = np.random.choice(["a", "b", "c"], size=100)
    data = pd.DataFrame({"x": x, "y": y, "b": b})
    if weight:
        data["weight"] = np.random.uniform(size=100)
    groupby = GroupBy(["b"])
    scales = {v: Continuous() for v in ["x", "y"]}

    data.loc[0, "x"] = np.nan
    data.loc[1, "y"] = np.nan
    data.loc[2, "b"] = np.nan
    if weight:
        data.loc[3, "weight"] = np.nan

    hist = Hist(
        stat=stat, common_bins=common_bins_vars, common_norm=common_norm_vars,
        cumulative=cumulative, discrete=discrete,
        bins=bins, binrange=binrange, binwidth=binwidth,
    )
    results = hist(data, groupby, orient, scales)
    assert not results.empty