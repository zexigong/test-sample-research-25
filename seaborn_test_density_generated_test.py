# Licensed under a 3-clause BSD style license - see LICENSE.rst
import numpy as np
import pandas as pd
import pytest
from numpy import nan
from numpy.testing import assert_array_equal, assert_allclose
from pandas import DataFrame
from pandas.testing import assert_frame_equal

from seaborn._core.groupby import GroupBy
from seaborn._core.scales import Continuous, Nominal
from seaborn._stats.density import KDE


def test_single_kde():
    x = np.random.normal(size=200)
    stat = KDE()
    data = pd.DataFrame({"x": x})
    gb = GroupBy(["x"])
    scales = dict(x=Continuous())
    out = stat(data, gb, "x", scales)
    assert len(out) == 200
    assert_array_equal(out["x"], x)
    assert not out["y"].isna().any()
    assert out["y"].sum() == pytest.approx(1)

    stat = KDE(gridsize=100)
    out = stat(data, gb, "x", scales)
    assert len(out) == 100
    assert not out["x"].isna().any()
    assert not out["y"].isna().any()
    assert out["y"].sum() == pytest.approx(1)


def test_single_kde_cumulative():
    x = np.random.normal(size=200)
    stat = KDE(cumulative=True)
    data = pd.DataFrame({"x": x})
    gb = GroupBy(["x"])
    scales = dict(x=Continuous())
    out = stat(data, gb, "x", scales)
    assert len(out) == 200
    assert_array_equal(out["x"], x)
    assert (out["y"] >= 0).all()
    assert (out["y"] <= 1).all()
    assert out["y"].iloc[-1] == pytest.approx(1)

    stat = KDE(gridsize=100, cumulative=True)
    out = stat(data, gb, "x", scales)
    assert len(out) == 100
    assert not out["x"].isna().any()
    assert (out["y"] >= 0).all()
    assert (out["y"] <= 1).all()
    assert out["y"].iloc[-1] == pytest.approx(1)


def test_minimal_data():
    # Single point without weight
    stat = KDE()
    data = pd.DataFrame({"x": [0]})
    gb = GroupBy(["x"])
    scales = dict(x=Continuous())
    out = stat(data, gb, "x", scales)
    assert len(out) == 0

    # Two points without weight
    stat = KDE()
    data = pd.DataFrame({"x": [0, 1]})
    gb = GroupBy(["x"])
    scales = dict(x=Continuous())
    out = stat(data, gb, "x", scales)
    assert len(out) == 2
    assert out["y"].sum() == pytest.approx(1)
    assert (out["y"] > 0).all()

    # Single point with weight
    stat = KDE()
    data = pd.DataFrame({"x": [0], "weight": [2]})
    gb = GroupBy(["x"])
    scales = dict(x=Continuous())
    out = stat(data, gb, "x", scales)
    assert len(out) == 0

    # Two points with weight
    stat = KDE()
    data = pd.DataFrame({"x": [0, 1], "weight": [2, 3]})
    gb = GroupBy(["x"])
    scales = dict(x=Continuous())
    out = stat(data, gb, "x", scales)
    assert len(out) == 2
    assert out["y"].sum() == pytest.approx(1)
    assert (out["y"] > 0).all()


def test_nan_data():
    # Single point without weight
    stat = KDE()
    data = pd.DataFrame({"x": [nan]})
    gb = GroupBy(["x"])
    scales = dict(x=Continuous())
    out = stat(data, gb, "x", scales)
    assert len(out) == 0

    # Two points without weight
    stat = KDE()
    data = pd.DataFrame({"x": [nan, 1]})
    gb = GroupBy(["x"])
    scales = dict(x=Continuous())
    out = stat(data, gb, "x", scales)
    assert len(out) == 1
    assert out["y"].sum() == pytest.approx(1)
    assert (out["y"] > 0).all()

    # Single point with weight
    stat = KDE()
    data = pd.DataFrame({"x": [nan], "weight": [2]})
    gb = GroupBy(["x"])
    scales = dict(x=Continuous())
    out = stat(data, gb, "x", scales)
    assert len(out) == 0

    # Two points with weight
    stat = KDE()
    data = pd.DataFrame({"x": [nan, 1], "weight": [2, 3]})
    gb = GroupBy(["x"])
    scales = dict(x=Continuous())
    out = stat(data, gb, "x", scales)
    assert len(out) == 1
    assert out["y"].sum() == pytest.approx(1)
    assert (out["y"] > 0).all()


def test_support_with_grid():
    x = np.random.uniform(size=20)
    stat = KDE(gridsize=10, cut=0)
    data = pd.DataFrame({"x": x})
    gb = GroupBy(["x"])
    scales = dict(x=Continuous())
    out = stat(data, gb, "x", scales)
    assert out.x.min() == pytest.approx(x.min())
    assert out.x.max() == pytest.approx(x.max())


def test_support_without_grid():
    x = np.random.uniform(size=20)
    stat = KDE(gridsize=None)
    data = pd.DataFrame({"x": x})
    gb = GroupBy(["x"])
    scales = dict(x=Continuous())
    out = stat(data, gb, "x", scales)
    assert_array_equal(out.x, x)


def test_single_kde_weighted():
    x = np.random.normal(size=200)
    w = np.random.uniform(size=200)
    stat = KDE()
    data = pd.DataFrame({"x": x, "weight": w})
    gb = GroupBy(["x"])
    scales = dict(x=Continuous())
    out = stat(data, gb, "x", scales)
    assert len(out) == 200
    assert_array_equal(out["x"], x)
    assert not out["y"].isna().any()
    assert out["y"].sum() == pytest.approx(1)

    stat = KDE(gridsize=100)
    out = stat(data, gb, "x", scales)
    assert len(out) == 100
    assert not out["x"].isna().any()
    assert not out["y"].isna().any()
    assert out["y"].sum() == pytest.approx(1)


def test_single_kde_cumulative_weighted():
    x = np.random.normal(size=200)
    w = np.random.uniform(size=200)
    stat = KDE(cumulative=True)
    data = pd.DataFrame({"x": x, "weight": w})
    gb = GroupBy(["x"])
    scales = dict(x=Continuous())
    out = stat(data, gb, "x", scales)
    assert len(out) == 200
    assert_array_equal(out["x"], x)
    assert (out["y"] >= 0).all()
    assert (out["y"] <= 1).all()
    assert out["y"].iloc[-1] == pytest.approx(1)

    stat = KDE(gridsize=100, cumulative=True)
    out = stat(data, gb, "x", scales)
    assert len(out) == 100
    assert not out["x"].isna().any()
    assert (out["y"] >= 0).all()
    assert (out["y"] <= 1).all()
    assert out["y"].iloc[-1] == pytest.approx(1)


def test_single_kde_weighted_minimal():
    # Single point with weight
    stat = KDE()
    data = pd.DataFrame({"x": [0], "weight": [2]})
    gb = GroupBy(["x"])
    scales = dict(x=Continuous())
    out = stat(data, gb, "x", scales)
    assert len(out) == 0

    # Two points with weight
    stat = KDE()
    data = pd.DataFrame({"x": [0, 1], "weight": [2, 3]})
    gb = GroupBy(["x"])
    scales = dict(x=Continuous())
    out = stat(data, gb, "x", scales)
    assert len(out) == 2
    assert out["y"].sum() == pytest.approx(1)
    assert (out["y"] > 0).all()


def test_single_kde_weighted_nan():
    # Single point with weight
    stat = KDE()
    data = pd.DataFrame({"x": [nan], "weight": [2]})
    gb = GroupBy(["x"])
    scales = dict(x=Continuous())
    out = stat(data, gb, "x", scales)
    assert len(out) == 0

    # Two points with weight
    stat = KDE()
    data = pd.DataFrame({"x": [nan, 1], "weight": [2, 3]})
    gb = GroupBy(["x"])
    scales = dict(x=Continuous())
    out = stat(data, gb, "x", scales)
    assert len(out) == 1
    assert out["y"].sum() == pytest.approx(1)
    assert (out["y"] > 0).all()


def test_single_kde_weighted_support_with_grid():
    x = np.random.uniform(size=20)
    w = np.random.uniform(size=20)
    stat = KDE(gridsize=10, cut=0)
    data = pd.DataFrame({"x": x, "weight": w})
    gb = GroupBy(["x"])
    scales = dict(x=Continuous())
    out = stat(data, gb, "x", scales)
    assert out.x.min() == pytest.approx(x.min())
    assert out.x.max() == pytest.approx(x.max())


def test_single_kde_weighted_support_without_grid():
    x = np.random.uniform(size=20)
    w = np.random.uniform(size=20)
    stat = KDE(gridsize=None)
    data = pd.DataFrame({"x": x, "weight": w})
    gb = GroupBy(["x"])
    scales = dict(x=Continuous())
    out = stat(data, gb, "x", scales)
    assert_array_equal(out.x, x)


def test_categorical_single():
    x = np.random.normal(size=200)
    y = np.random.choice(["a", "b", "c"], 200)
    stat = KDE()
    data = pd.DataFrame({"x": x, "y": y})
    gb = GroupBy(["x", "y"])
    scales = dict(x=Continuous(), y=Nominal())
    out = stat(data, gb, "x", scales)
    assert out.groupby("y")["y"].count().equals(data["y"].value_counts())
    assert out.groupby("y")["y"].sum().equals(pd.Series([1, 1, 1], index=["a", "b", "c"]))


def test_categorical_single_weighted():
    x = np.random.normal(size=200)
    y = np.random.choice(["a", "b", "c"], 200)
    w = np.random.uniform(size=200)
    stat = KDE()
    data = pd.DataFrame({"x": x, "y": y, "weight": w})
    gb = GroupBy(["x", "y"])
    scales = dict(x=Continuous(), y=Nominal())
    out = stat(data, gb, "x", scales)
    assert out.groupby("y")["y"].count().equals(data["y"].value_counts())
    assert out.groupby("y")["y"].sum().equals(pd.Series([1, 1, 1], index=["a", "b", "c"]))


def test_categorical_single_with_grid():
    x = np.random.uniform(size=200)
    y = np.random.choice(["a", "b", "c"], 200)
    stat = KDE(gridsize=100)
    data = pd.DataFrame({"x": x, "y": y})
    gb = GroupBy(["x", "y"])
    scales = dict(x=Continuous(), y=Nominal())
    out = stat(data, gb, "x", scales)
    assert len(out) == 300
    assert out.groupby("y")["y"].sum().equals(pd.Series([1, 1, 1], index=["a", "b", "c"]))


def test_categorical_single_with_grid_weighted():
    x = np.random.uniform(size=200)
    y = np.random.choice(["a", "b", "c"], 200)
    w = np.random.uniform(size=200)
    stat = KDE(gridsize=100)
    data = pd.DataFrame({"x": x, "y": y, "weight": w})
    gb = GroupBy(["x", "y"])
    scales = dict(x=Continuous(), y=Nominal())
    out = stat(data, gb, "x", scales)
    assert len(out) == 300
    assert out.groupby("y")["y"].sum().equals(pd.Series([1, 1, 1], index=["a", "b", "c"]))


def test_categorical_single_within_grid():
    x = np.random.uniform(size=200)
    y = np.random.choice(["a", "b", "c"], 200)
    stat = KDE(gridsize=100, common_grid=["y"])
    data = pd.DataFrame({"x": x, "y": y})
    gb = GroupBy(["x", "y"])
    scales = dict(x=Continuous(), y=Nominal())
    out = stat(data, gb, "x", scales)
    assert len(out) == 300
    assert out.groupby("y")["y"].sum().equals(pd.Series([1, 1, 1], index=["a", "b", "c"]))


def test_categorical_single_within_grid_weighted():
    x = np.random.uniform(size=200)
    y = np.random.choice(["a", "b", "c"], 200)
    w = np.random.uniform(size=200)
    stat = KDE(gridsize=100, common_grid=["y"])
    data = pd.DataFrame({"x": x, "y": y, "weight": w})
    gb = GroupBy(["x", "y"])
    scales = dict(x=Continuous(), y=Nominal())
    out = stat(data, gb, "x", scales)
    assert len(out) == 300
    assert out.groupby("y")["y"].sum().equals(pd.Series([1, 1, 1], index=["a", "b", "c"]))


def test_categorical_double():
    x = np.random.normal(size=200)
    y = np.random.choice(["a", "b", "c"], 200)
    z = np.random.choice(["A", "B", "C"], 200)
    stat = KDE()
    data = pd.DataFrame({"x": x, "y": y, "z": z})
    gb = GroupBy(["x", "y", "z"])
    scales = dict(x=Continuous(), y=Nominal(), z=Nominal())
    out = stat(data, gb, "x", scales)
    assert out.groupby(["y", "z"])["y"].count().equals(data.groupby(["y", "z"])["y"].count())
    assert out.groupby(["y", "z"])["y"].sum().equals(pd.Series([1, 1, 1, 1, 1, 1, 1, 1, 1], index=[
        ("a", "A"), ("a", "B"), ("a", "C"),
        ("b", "A"), ("b", "B"), ("b", "C"),
        ("c", "A"), ("c", "B"), ("c", "C"),
    ]))


def test_categorical_double_weighted():
    x = np.random.normal(size=200)
    y = np.random.choice(["a", "b", "c"], 200)
    z = np.random.choice(["A", "B", "C"], 200)
    w = np.random.uniform(size=200)
    stat = KDE()
    data = pd.DataFrame({"x": x, "y": y, "z": z, "weight": w})
    gb = GroupBy(["x", "y", "z"])
    scales = dict(x=Continuous(), y=Nominal(), z=Nominal())
    out = stat(data, gb, "x", scales)
    assert out.groupby(["y", "z"])["y"].count().equals(data.groupby(["y", "z"])["y"].count())
    assert out.groupby(["y", "z"])["y"].sum().equals(pd.Series([1, 1, 1, 1, 1, 1, 1, 1, 1], index=[
        ("a", "A"), ("a", "B"), ("a", "C"),
        ("b", "A"), ("b", "B"), ("b", "C"),
        ("c", "A"), ("c", "B"), ("c", "C"),
    ]))


def test_categorical_double_with_grid():
    x = np.random.uniform(size=200)
    y = np.random.choice(["a", "b", "c"], 200)
    z = np.random.choice(["A", "B", "C"], 200)
    stat = KDE(gridsize=100)
    data = pd.DataFrame({"x": x, "y": y, "z": z})
    gb = GroupBy(["x", "y", "z"])
    scales = dict(x=Continuous(), y=Nominal(), z=Nominal())
    out = stat(data, gb, "x", scales)
    assert len(out) == 900
    assert out.groupby(["y", "z"])["y"].sum().equals(pd.Series([1, 1, 1, 1, 1, 1, 1, 1, 1], index=[
        ("a", "A"), ("a", "B"), ("a", "C"),
        ("b", "A"), ("b", "B"), ("b", "C"),
        ("c", "A"), ("c", "B"), ("c", "C"),
    ]))


def test_categorical_double_with_grid_weighted():
    x = np.random.uniform(size=200)
    y = np.random.choice(["a", "b", "c"], 200)
    z = np.random.choice(["A", "B", "C"], 200)
    w = np.random.uniform(size=200)
    stat = KDE(gridsize=100)
    data = pd.DataFrame({"x": x, "y": y, "z": z, "weight": w})
    gb = GroupBy(["x", "y", "z"])
    scales = dict(x=Continuous(), y=Nominal(), z=Nominal())
    out = stat(data, gb, "x", scales)
    assert len(out) == 900
    assert out.groupby(["y", "z"])["y"].sum().equals(pd.Series([1, 1, 1, 1, 1, 1, 1, 1, 1], index=[
        ("a", "A"), ("a", "B"), ("a", "C"),
        ("b", "A"), ("b", "B"), ("b", "C"),
        ("c", "A"), ("c", "B"), ("c", "C"),
    ]))


def test_categorical_double_within_grid():
    x = np.random.uniform(size=200)
    y = np.random.choice(["a", "b", "c"], 200)
    z = np.random.choice(["A", "B", "C"], 200)
    stat = KDE(gridsize=100, common_grid=["y"])
    data = pd.DataFrame({"x": x, "y": y, "z": z})
    gb = GroupBy(["x", "y", "z"])
    scales = dict(x=Continuous(), y=Nominal(), z=Nominal())
    out = stat(data, gb, "x", scales)
    assert len(out) == 900
    assert out.groupby(["y", "z"])["y"].sum().equals(pd.Series([1, 1, 1, 1, 1, 1, 1, 1, 1], index=[
        ("a", "A"), ("a", "B"), ("a", "C"),
        ("b", "A"), ("b", "B"), ("b", "C"),
        ("c", "A"), ("c", "B"), ("c", "C"),
    ]))


def test_categorical_double_within_grid_weighted():
    x = np.random.uniform(size=200)
    y = np.random.choice(["a", "b", "c"], 200)
    z = np.random.choice(["A", "B", "C"], 200)
    w = np.random.uniform(size=200)
    stat = KDE(gridsize=100, common_grid=["y"])
    data = pd.DataFrame({"x": x, "y": y, "z": z, "weight": w})
    gb = GroupBy(["x", "y", "z"])
    scales = dict(x=Continuous(), y=Nominal(), z=Nominal())
    out = stat(data, gb, "x", scales)
    assert len(out) == 900
    assert out.groupby(["y", "z"])["y"].sum().equals(pd.Series([1, 1, 1, 1, 1, 1, 1, 1, 1], index=[
        ("a", "A"), ("a", "B"), ("a", "C"),
        ("b", "A"), ("b", "B"), ("b", "C"),
        ("c", "A"), ("c", "B"), ("c", "C"),
    ]))


def test_common_norm_true():
    x = np.random.normal(size=200)
    y = np.random.choice(["a", "b", "c"], 200)
    stat = KDE(common_norm=True)
    data = pd.DataFrame({"x": x, "y": y})
    gb = GroupBy(["x", "y"])
    scales = dict(x=Continuous(), y=Nominal())
    out = stat(data, gb, "x", scales)
    assert out.y.sum() == pytest.approx(1)


def test_common_norm_true_weighted():
    x = np.random.normal(size=200)
    y = np.random.choice(["a", "b", "c"], 200)
    w = np.random.uniform(size=200)
    stat = KDE(common_norm=True)
    data = pd.DataFrame({"x": x, "y": y, "weight": w})
    gb = GroupBy(["x", "y"])
    scales = dict(x=Continuous(), y=Nominal())
    out = stat(data, gb, "x", scales)
    assert out.y.sum() == pytest.approx(1)


def test_common_norm_false():
    x = np.random.normal(size=200)
    y = np.random.choice(["a", "b", "c"], 200)
    stat = KDE(common_norm=False)
    data = pd.DataFrame({"x": x, "y": y})
    gb = GroupBy(["x", "y"])
    scales = dict(x=Continuous(), y=Nominal())
    out = stat(data, gb, "x", scales)
    assert out.groupby("y").y.sum().equals(pd.Series([1, 1, 1], index=["a", "b", "c"]))


def test_common_norm_false_weighted():
    x = np.random.normal(size=200)
    y = np.random.choice(["a", "b", "c"], 200)
    w = np.random.uniform(size=200)
    stat = KDE(common_norm=False)
    data = pd.DataFrame({"x": x, "y": y, "weight": w})
    gb = GroupBy(["x", "y"])
    scales = dict(x=Continuous(), y=Nominal())
    out = stat(data, gb, "x", scales)
    assert out.groupby("y").y.sum().equals(pd.Series([1, 1, 1], index=["a", "b", "c"]))


def test_common_norm_within():
    x = np.random.normal(size=200)
    y = np.random.choice(["a", "b", "c"], 200)
    z = np.random.choice(["A", "B", "C"], 200)
    stat = KDE(common_norm=["y"])
    data = pd.DataFrame({"x": x, "y": y, "z": z})
    gb = GroupBy(["x", "y", "z"])
    scales = dict(x=Continuous(), y=Nominal(), z=Nominal())
    out = stat(data, gb, "x", scales)
    assert out.groupby("y").y.sum().equals(pd.Series([1, 1, 1], index=["a", "b", "c"]))


def test_common_norm_within_weighted():
    x = np.random.normal(size=200)
    y = np.random.choice(["a", "b", "c"], 200)
    z = np.random.choice(["A", "B", "C"], 200)
    w = np.random.uniform(size=200)
    stat = KDE(common_norm=["y"])
    data = pd.DataFrame({"x": x, "y": y, "z": z, "weight": w})
    gb = GroupBy(["x", "y", "z"])
    scales = dict(x=Continuous(), y=Nominal(), z=Nominal())
    out = stat(data, gb, "x", scales)
    assert out.groupby("y").y.sum().equals(pd.Series([1, 1, 1], index=["a", "b", "c"]))


def test_common_norm_within_weighted_undefined():
    x = np.random.normal(size=200)
    y = np.random.choice(["a", "b", "c"], 200)
    z = np.random.choice(["A", "B", "C"], 200)
    w = np.random.uniform(size=200)
    stat = KDE(common_norm=["y", "u"])
    data = pd.DataFrame({"x": x, "y": y, "z": z, "weight": w})
    gb = GroupBy(["x", "y", "z"])
    scales = dict(x=Continuous(), y=Nominal(), z=Nominal())
    with pytest.warns(UserWarning, match="Undefined variable"):
        out = stat(data, gb, "x", scales)
    assert out.groupby("y").y.sum().equals(pd.Series([1, 1, 1], index=["a", "b", "c"]))


def test_common_norm_within_grid():
    x = np.random.normal(size=200)
    y = np.random.choice(["a", "b", "c"], 200)
    z = np.random.choice(["A", "B", "C"], 200)
    stat = KDE(common_norm=["y", "z"])
    data = pd.DataFrame({"x": x, "y": y, "z": z})
    gb = GroupBy(["x", "y", "z"])
    scales = dict(x=Continuous(), y=Nominal(), z=Nominal())
    out = stat(data, gb, "x", scales)
    assert out.groupby(["y", "z"]).y.sum().equals(pd.Series([1, 1, 1, 1, 1, 1, 1, 1, 1], index=[
        ("a", "A"), ("a", "B"), ("a", "C"),
        ("b", "A"), ("b", "B"), ("b", "C"),
        ("c", "A"), ("c", "B"), ("c", "C"),
    ]))


def test_common_norm_within_grid_weighted():
    x = np.random.normal(size=200)
    y = np.random.choice(["a", "b", "c"], 200)
    z = np.random.choice(["A", "B", "C"], 200)
    w = np.random.uniform(size=200)
    stat = KDE(common_norm=["y", "z"])
    data = pd.DataFrame({"x": x, "y": y, "z": z, "weight": w})
    gb = GroupBy(["x", "y", "z"])
    scales = dict(x=Continuous(), y=Nominal(), z=Nominal())
    out = stat(data, gb, "x", scales)
    assert out.groupby(["y", "z"]).y.sum().equals(pd.Series([1, 1, 1, 1, 1, 1, 1, 1, 1], index=[
        ("a", "A"), ("a", "B"), ("a", "C"),
        ("b", "A"), ("b", "B"), ("b", "C"),
        ("c", "A"), ("c", "B"), ("c", "C"),
    ]))


def test_common_norm_within_grid_weighted_undefined():
    x = np.random.normal(size=200)
    y = np.random.choice(["a", "b", "c"], 200)
    z = np.random.choice(["A", "B", "C"], 200)
    w = np.random.uniform(size=200)
    stat = KDE(common_norm=["y", "z", "u"])
    data = pd.DataFrame({"x": x, "y": y, "z": z, "weight": w})
    gb = GroupBy(["x", "y", "z"])
    scales = dict(x=Continuous(), y=Nominal(), z=Nominal())
    with pytest.warns(UserWarning, match="Undefined variable"):
        out = stat(data, gb, "x", scales)
    assert out.groupby(["y", "z"]).y.sum().equals(pd.Series([1, 1, 1, 1, 1, 1, 1, 1, 1], index=[
        ("a", "A"), ("a", "B"), ("a", "C"),
        ("b", "A"), ("b", "B"), ("b", "C"),
        ("c", "A"), ("c", "B"), ("c", "C"),
    ]))


def test_common_norm_false_within_grid():
    x = np.random.normal(size=200)
    y = np.random.choice(["a", "b", "c"], 200)
    z = np.random.choice(["A", "B", "C"], 200)
    stat = KDE(common_norm=False)
    data = pd.DataFrame({"x": x, "y": y, "z": z})
    gb = GroupBy(["x", "y", "z"])
    scales = dict(x=Continuous(), y=Nominal(), z=Nominal())
    out = stat(data, gb, "x", scales)
    assert out.groupby(["y", "z"]).y.sum().equals(pd.Series([1, 1, 1, 1, 1, 1, 1, 1, 1], index=[
        ("a", "A"), ("a", "B"), ("a", "C"),
        ("b", "A"), ("b", "B"), ("b", "C"),
        ("c", "A"), ("c", "B"), ("c", "C"),
    ]))


def test_common_norm_false_within_grid_weighted():
    x = np.random.normal(size=200)
    y = np.random.choice(["a", "b", "c"], 200)
    z = np.random.choice(["A", "B", "C"], 200)
    w = np.random.uniform(size=200)
    stat = KDE(common_norm=False)
    data = pd.DataFrame({"x": x, "y": y, "z": z, "weight": w})
    gb = GroupBy(["x", "y", "z"])
    scales = dict(x=Continuous(), y=Nominal(), z=Nominal())
    out = stat(data, gb, "x", scales)
    assert out.groupby(["y", "z"]).y.sum().equals(pd.Series([1, 1, 1, 1, 1, 1, 1, 1, 1], index=[
        ("a", "A"), ("a", "B"), ("a", "C"),
        ("b", "A"), ("b", "B"), ("b", "C"),
        ("c", "A"), ("c", "B"), ("c", "C"),
    ]))


def test_common_norm_false_within_grid_weighted_undefined():
    x = np.random.normal(size=200)
    y = np.random.choice(["a", "b", "c"], 200)
    z = np.random.choice(["A", "B", "C"], 200)
    w = np.random.uniform(size=200)
    stat = KDE(common_norm=False)
    data = pd.DataFrame({"x": x, "y": y, "z": z, "weight": w})
    gb = GroupBy(["x", "y", "z"])
    scales = dict(x=Continuous(), y=Nominal(), z=Nominal())
    with pytest.warns(None):
        out = stat(data, gb, "x", scales)
    assert out.groupby(["y", "z"]).y.sum().equals(pd.Series([1, 1, 1, 1, 1, 1, 1, 1, 1], index=[
        ("a", "A"), ("a", "B"), ("a", "C"),
        ("b", "A"), ("b", "B"), ("b", "C"),
        ("c", "A"), ("c", "B"), ("c", "C"),
    ]))


def test_common_grid_true():
    x = np.random.normal(size=200)
    y = np.random.choice(["a", "b", "c"], 200)
    stat = KDE(gridsize=100, common_grid=True)
    data = pd.DataFrame({"x": x, "y": y})
    gb = GroupBy(["x", "y"])
    scales = dict(x=Continuous(), y=Nominal())
    out = stat(data, gb, "x", scales)
    assert len(out) == 300
    assert out.groupby("y").y.sum().equals(pd.Series([1, 1, 1], index=["a", "b", "c"]))


def test_common_grid_true_weighted():
    x = np.random.normal(size=200)
    y = np.random.choice(["a", "b", "c"], 200)
    w = np.random.uniform(size=200)
    stat = KDE(gridsize=100, common_grid=True)
    data = pd.DataFrame({"x": x, "y": y, "weight": w})
    gb = GroupBy(["x", "y"])
    scales = dict(x=Continuous(), y=Nominal())
    out = stat(data, gb, "x", scales)
    assert len(out) == 300
    assert out.groupby("y").y.sum().equals(pd.Series([1, 1, 1], index=["a", "b", "c"]))


def test_common_grid_false():
    x = np.random.normal(size=200)
    y = np.random.choice(["a", "b", "c"], 200)
    stat = KDE(gridsize=100, common_grid=False)
    data = pd.DataFrame({"x": x, "y": y})
    gb = GroupBy(["x", "y"])
    scales = dict(x=Continuous(), y=Nominal())
    out = stat(data, gb, "x", scales)
    assert len(out) == 300
    assert out.groupby("y").y.sum().equals(pd.Series([1, 1, 1], index=["a", "b", "c"]))


def test_common_grid_false_weighted():
    x = np.random.normal(size=200)
    y = np.random.choice(["a", "b", "c"], 200)
    w = np.random.uniform(size=200)
    stat = KDE(gridsize=100, common_grid=False)
    data = pd.DataFrame({"x": x, "y": y, "weight": w})
    gb = GroupBy(["x", "y"])
    scales = dict(x=Continuous(), y=Nominal())
    out = stat(data, gb, "x", scales)
    assert len(out) == 300
    assert out.groupby("y").y.sum().equals(pd.Series([1, 1, 1], index=["a", "b", "c"]))


def test_common_grid_within():
    x = np.random.normal(size=200)
    y = np.random.choice(["a", "b", "c"], 200)
    z = np.random.choice(["A", "B", "C"], 200)
    stat = KDE(gridsize=100, common_grid=["y"])
    data = pd.DataFrame({"x": x, "y": y, "z": z})
    gb = GroupBy(["x", "y", "z"])
    scales = dict(x=Continuous(), y=Nominal(), z=Nominal())
    out = stat(data, gb, "x", scales)
    assert len(out) == 900
    assert out.groupby(["y", "z"]).y.sum().equals(pd.Series([1, 1, 1, 1, 1, 1, 1, 1, 1], index=[
        ("a", "A"), ("a", "B"), ("a", "C"),
        ("b", "A"), ("b", "B"), ("b", "C"),
        ("c", "A"), ("c", "B"), ("c", "C"),
    ]))


def test_common_grid_within_weighted():
    x = np.random.normal(size=200)
    y = np.random.choice(["a", "b", "c"], 200)
    z = np.random.choice(["A", "B", "C"], 200)
    w = np.random.uniform(size=200)
    stat = KDE(gridsize=100, common_grid=["y"])
    data = pd.DataFrame({"x": x, "y": y, "z": z, "weight": w})
    gb = GroupBy(["x", "y", "z"])
    scales = dict(x=Continuous(), y=Nominal(), z=Nominal())
    out = stat(data, gb, "x", scales)
    assert len(out) == 900
    assert out.groupby(["y", "z"]).y.sum().equals(pd.Series([1, 1, 1, 1, 1, 1, 1, 1, 1], index=[
        ("a", "A"), ("a", "B"), ("a", "C"),
        ("b", "A"), ("b", "B"), ("b", "C"),
        ("c", "A"), ("c", "B"), ("c", "C"),
    ]))


def test_common_grid_within_weighted_undefined():
    x = np.random.normal(size=200)
    y = np.random.choice(["a", "b", "c"], 200)
    z = np.random.choice(["A", "B", "C"], 200)
    w = np.random.uniform(size=200)
    stat = KDE(gridsize=100, common_grid=["y", "u"])
    data = pd.DataFrame({"x": x, "y": y, "z": z, "weight": w})
    gb = GroupBy(["x", "y", "z"])
    scales = dict(x=Continuous(), y=Nominal(), z=Nominal())
    with pytest.warns(UserWarning, match="Undefined variable"):
        out = stat(data, gb, "x", scales)
    assert len(out) == 900
    assert out.groupby(["y", "z"]).y.sum().equals(pd.Series([1, 1, 1, 1, 1, 1, 1, 1, 1], index=[
        ("a", "A"), ("a", "B"), ("a", "C"),
        ("b", "A"), ("b", "B"), ("b", "C"),
        ("c", "A"), ("c", "B"), ("c", "C"),
    ]))


def test_common_grid_within_grid():
    x = np.random.normal(size=200)
    y = np.random.choice(["a", "b", "c"], 200)
    z = np.random.choice(["A", "B", "C"], 200)
    stat = KDE(gridsize=100, common_grid=["y", "z"])
    data = pd.DataFrame({"x": x, "y": y, "z": z})
    gb = GroupBy(["x", "y", "z"])
    scales = dict(x=Continuous(), y=Nominal(), z=Nominal())
    out = stat(data, gb, "x", scales)
    assert len(out) == 900
    assert out.groupby(["y", "z"]).y.sum().equals(pd.Series([1, 1, 1, 1, 1, 1, 1, 1, 1], index=[
        ("a", "A"), ("a", "B"), ("a", "C"),
        ("b", "A"), ("b", "B"), ("b", "C"),
        ("c", "A"), ("c", "B"), ("c", "C"),
    ]))


def test_common_grid_within_grid_weighted():
    x = np.random.normal(size=200)
    y = np.random.choice(["a", "b", "c"], 200)
    z = np.random.choice(["A", "B", "C"], 200)
    w = np.random.uniform(size=200)
    stat = KDE(gridsize=100, common_grid=["y", "z"])
    data = pd.DataFrame({"x": x, "y": y, "z": z, "weight": w})
    gb = GroupBy(["x", "y", "z"])
    scales = dict(x=Continuous(), y=Nominal(), z=Nominal())
    out = stat(data, gb, "x", scales)
    assert len(out) == 900
    assert out.groupby(["y", "z"]).y.sum().equals(pd.Series([1, 1, 1, 1, 1, 1, 1, 1, 1], index=[
        ("a", "A"), ("a", "B"), ("a", "C"),
        ("b", "A"), ("b", "B"), ("b", "C"),
        ("c", "A"), ("c", "B"), ("c", "C"),
    ]))


def test_common_grid_within_grid_weighted_undefined():
    x = np.random.normal(size=200)
    y = np.random.choice(["a", "b", "c"], 200)
    z = np.random.choice(["A", "B", "C"], 200)
    w = np.random.uniform(size=200)
    stat = KDE(gridsize=100, common_grid=["y", "z", "u"])
    data = pd.DataFrame({"x": x, "y": y, "z": z, "weight": w})
    gb = GroupBy(["x", "y", "z"])
    scales = dict(x=Continuous(), y=Nominal(), z=Nominal())
    with pytest.warns(UserWarning, match="Undefined variable"):
        out = stat(data, gb, "x", scales)
    assert len(out) == 900
    assert out.groupby(["y", "z"]).y.sum().equals(pd.Series([1, 1, 1, 1, 1, 1, 1, 1, 1], index=[
        ("a", "A"), ("a", "B"), ("a", "C"),
        ("b", "A"), ("b", "B"), ("b", "C"),
        ("c", "A"), ("c", "B"), ("c", "C"),
    ]))


def test_common_grid_false_within_grid():
    x = np.random.normal(size=200)
    y = np.random.choice(["a", "b", "c"], 200)
    z = np.random.choice(["A", "B", "C"], 200)
    stat = KDE(gridsize=100, common_grid=False)
    data = pd.DataFrame({"x": x, "y": y, "z": z})
    gb = GroupBy(["x", "y", "z"])
    scales = dict(x=Continuous(), y=Nominal(), z=Nominal())
    out = stat(data, gb, "x", scales)
    assert len(out) == 900
    assert out.groupby(["y", "z"]).y.sum().equals(pd.Series([1, 1, 1, 1, 1, 1, 1, 1, 1], index=[
        ("a", "A"), ("a", "B"), ("a", "C"),
        ("b", "A"), ("b", "B"), ("b", "C"),
        ("c", "A"), ("c", "B"), ("c", "C"),
    ]))


def test_common_grid_false_within_grid_weighted():
    x = np.random.normal(size=200)
    y = np.random.choice(["a", "b", "c"], 200)
    z = np.random.choice(["A", "B", "C"], 200)
    w = np.random.uniform(size=200)
    stat = KDE(gridsize=100, common_grid=False)
    data = pd.DataFrame({"x": x, "y": y, "z": z, "weight": w})
    gb = GroupBy(["x", "y", "z"])
    scales = dict(x=Continuous(), y=Nominal(), z=Nominal())
    out = stat(data, gb, "x", scales)
    assert len(out) == 900
    assert out.groupby(["y", "z"]).y.sum().equals(pd.Series([1, 1, 1, 1, 1, 1, 1, 1, 1], index=[
        ("a", "A"), ("a", "B"), ("a", "C"),
        ("b", "A"), ("b", "B"), ("b", "C"),
        ("c", "A"), ("c", "B"), ("c", "C"),
    ]))


def test_common_grid_false_within_grid_weighted_undefined():
    x = np.random.normal(size=200)
    y = np.random.choice(["a", "b", "c"], 200)
    z = np.random.choice(["A", "B", "C"], 200)
    w = np.random.uniform(size=200)
    stat = KDE(gridsize=100, common_grid=False)
    data = pd.DataFrame({"x": x, "y": y, "z": z, "weight": w})
    gb = GroupBy(["x", "y", "z"])
    scales = dict(x=Continuous(), y=Nominal(), z=Nominal())
    with pytest.warns(None):
        out = stat(data, gb, "x", scales)
    assert len(out) == 900
    assert out.groupby(["y", "z"]).y.sum().equals(pd.Series([1, 1, 1, 1, 1, 1, 1, 1, 1], index=[
        ("a", "A"), ("a", "B"), ("a", "C"),
        ("b", "A"), ("b", "B"), ("b", "C"),
        ("c", "A"), ("c", "B"), ("c", "C"),
    ]))


def test_data_without_group():
    x = np.random.normal(size=200)
    stat = KDE()
    data = pd.DataFrame({"x": x})
    gb = GroupBy([])
    scales = dict(x=Continuous())
    out = stat(data, gb, "x", scales)
    assert len(out) == 200
    assert_array_equal(out["x"], x)
    assert not out["y"].isna().any()
    assert out["y"].sum() == pytest.approx(1)


def test_data_without_group_weighted():
    x = np.random.normal(size=200)
    w = np.random.uniform(size=200)
    stat = KDE()
    data = pd.DataFrame({"x": x, "weight": w})
    gb = GroupBy([])
    scales = dict(x=Continuous())
    out = stat(data, gb, "x", scales)
    assert len(out) == 200
    assert_array_equal(out["x"], x)
    assert not out["y"].isna().any()
    assert out["y"].sum() == pytest.approx(1)


def test_data_without_group_with_grid():
    x = np.random.normal(size=200)
    stat = KDE(gridsize=100)
    data = pd.DataFrame({"x": x})
    gb = GroupBy([])
    scales = dict(x=Continuous())
    out = stat(data, gb, "x", scales)
    assert len(out) == 100
    assert not out["x"].isna().any()
    assert not out["y"].isna().any()
    assert out["y"].sum() == pytest.approx(1)


def test_data_without_group_with_grid_weighted():
    x = np.random.normal(size=200)
    w = np.random.uniform(size=200)
    stat = KDE(gridsize=100)
    data = pd.DataFrame({"x": x, "weight": w})
    gb = GroupBy([])
    scales = dict(x=Continuous())
    out = stat(data, gb, "x", scales)
    assert len(out) == 100
    assert not out["x"].isna().any()
    assert not out["y"].isna().any()
    assert out["y"].sum() == pytest.approx(1)


def test_data_without_group_cumulative():
    x = np.random.normal(size=200)
    stat = KDE(cumulative=True)
    data = pd.DataFrame({"x": x})
    gb = GroupBy([])
    scales = dict(x=Continuous())
    out = stat(data, gb, "x", scales)
    assert len(out) == 200
    assert_array_equal(out["x"], x)
    assert (out["y"] >= 0).all()
    assert (out["y"] <= 1).all()
    assert out["y"].iloc[-1] == pytest.approx(1)


def test_data_without_group_cumulative_weighted():
    x = np.random.normal(size=200)
    w = np.random.uniform(size=200)
    stat = KDE(cumulative=True)
    data = pd.DataFrame({"x": x, "weight": w})
    gb = GroupBy([])
    scales = dict(x=Continuous())
    out = stat(data, gb, "x", scales)
    assert len(out) == 200
    assert_array_equal(out["x"], x)
    assert (out["y"] >= 0).all()
    assert (out["y"] <= 1).all()
    assert out["y"].iloc[-1] == pytest.approx(1)


def test_data_without_group_with_grid_cumulative():
    x = np.random.normal(size=200)
    stat = KDE(gridsize=100, cumulative=True)
    data = pd.DataFrame({"x": x})
    gb = GroupBy([])
    scales = dict(x=Continuous())
    out = stat(data, gb, "x", scales)
    assert len(out) == 100
    assert not out["x"].isna().any()
    assert (out["y"] >= 0).all()
    assert (out["y"] <= 1).all()
    assert out["y"].iloc[-1] == pytest.approx(1)


def test_data_without_group_with_grid_cumulative_weighted():
    x = np.random.normal(size=200)
    w = np.random.uniform(size=200)
    stat = KDE(gridsize=100, cumulative=True)
    data = pd.DataFrame({"x": x, "weight": w})
    gb = GroupBy([])
    scales = dict(x=Continuous())
    out = stat(data, gb, "x", scales)
    assert len(out) == 100
    assert not out["x"].isna().any()
    assert (out["y"] >= 0).all()
    assert (out["y"] <= 1).all()
    assert out["y"].iloc[-1] == pytest.approx(1)


def test_data_without_group_minimal():
    # Single point without weight
    stat = KDE()
    data = pd.DataFrame({"x": [0]})
    gb = GroupBy([])
    scales = dict(x=Continuous())
    out = stat(data, gb, "x", scales)
    assert len(out) == 0

    # Two points without weight
    stat = KDE()
    data = pd.DataFrame({"x": [0, 1]})
    gb = GroupBy([])
    scales = dict(x=Continuous())
    out = stat(data, gb, "x", scales)
    assert len(out) == 2
    assert out["y"].sum() == pytest.approx(1)
    assert (out["y"] > 0).all()

    # Single point with weight
    stat = KDE()
    data = pd.DataFrame({"x": [0], "weight": [2]})
    gb = GroupBy([])
    scales = dict(x=Continuous())
    out = stat(data, gb, "x", scales)
    assert len(out) == 0

    # Two points with weight
    stat = KDE()
    data = pd.DataFrame({"x": [0, 1], "weight": [2, 3]})
    gb = GroupBy([])
    scales = dict(x=Continuous())
    out = stat(data, gb, "x", scales)
    assert len(out) == 2
    assert out["y"].sum() == pytest.approx(1)
    assert (out["y"] > 0).all()


def test_data_without_group_nan():
    # Single point without weight
    stat = KDE()
    data = pd.DataFrame({"x": [nan]})
    gb = GroupBy([])
    scales = dict(x=Continuous())
    out = stat(data, gb, "x", scales)
    assert len(out) == 0

    # Two points without weight
    stat = KDE()
    data = pd.DataFrame({"x": [nan, 1]})
    gb = GroupBy([])
    scales = dict(x=Continuous())
    out = stat(data, gb, "x", scales)
    assert len(out) == 1
    assert out["y"].sum() == pytest.approx(1)
    assert (out["y"] > 0).all()

    # Single point with weight
    stat = KDE()
    data = pd.DataFrame({"x": [nan], "weight": [2]})
    gb = GroupBy([])
    scales = dict(x=Continuous())
    out = stat(data, gb, "x", scales)
    assert len(out) == 0

    # Two points with weight
    stat = KDE()
    data = pd.DataFrame({"x": [nan, 1], "weight": [2, 3]})
    gb = GroupBy([])
    scales = dict(x=Continuous())
    out = stat(data, gb, "x", scales)
    assert len(out) == 1
    assert out["y"].sum() == pytest.approx(1)
    assert (out["y"] > 0).all()


def test_data_without_group_weighted():
    # Single point without weight
    stat = KDE()
    data = pd.DataFrame({"x": [0], "weight": [2]})
    gb = GroupBy([])
    scales = dict(x=Continuous())
    out = stat(data, gb, "x", scales)
    assert len(out) == 0

    # Two points without weight
    stat = KDE()
    data = pd.DataFrame({"x": [0, 1], "weight": [2, 3]})
    gb = GroupBy([])
    scales = dict(x=Continuous())
    out = stat(data, gb, "x", scales)
    assert len(out) == 2
    assert out["y"].sum() == pytest.approx(1)
    assert (out["y"] > 0).all()

    # Single point with weight
    stat = KDE()
    data = pd.DataFrame({"x": [0], "weight": [2]})
    gb = GroupBy([])
    scales = dict(x=Continuous())
    out = stat(data, gb, "x", scales)
    assert len(out) == 0

    # Two points with weight
    stat = KDE()
    data = pd.DataFrame({"x": [0, 1], "weight": [2, 3]})
    gb = GroupBy([])
    scales = dict(x=Continuous())
    out = stat(data, gb, "x", scales)
    assert len(out) == 2
    assert out["y"].sum() == pytest.approx(1)
    assert (out["y"] > 0).all()


def test_data_without_group_weighted_nan():
    # Single point without weight
    stat = KDE()
    data = pd.DataFrame({"x": [nan], "weight": [2]})
    gb = GroupBy([])
    scales = dict(x=Continuous())
    out = stat(data, gb, "x", scales)
    assert len(out) == 0

    # Two points without weight
    stat = KDE()
    data = pd.DataFrame({"x": [nan, 1], "weight": [2, 3]})
    gb = GroupBy([])
    scales = dict(x=Continuous())
    out = stat(data, gb, "x", scales)
    assert len(out) == 1
    assert out["y"].sum() == pytest.approx(1)
    assert (out["y"] > 0).all()

    # Single point with weight
    stat = KDE()
    data = pd.DataFrame({"x": [nan], "weight": [2]})
    gb = GroupBy([])
    scales = dict(x=Continuous())
    out = stat(data, gb, "x", scales)
    assert len(out) == 0

    # Two points with weight
    stat = KDE()
    data = pd.DataFrame({"x": [nan, 1], "weight": [2, 3]})
    gb = GroupBy([])
    scales = dict(x=Continuous())
    out = stat(data, gb, "x", scales)
    assert len(out) == 1
    assert out["y"].sum() == pytest.approx(1)
    assert (out["y"] > 0).all()


def test_data_without_group_support_with_grid():
    x = np.random.uniform(size=20)
    stat = KDE(gridsize=10, cut=0)
    data = pd.DataFrame({"x": x})
    gb = GroupBy([])
    scales = dict(x=Continuous())
    out = stat(data, gb, "x", scales)
    assert out.x.min() == pytest.approx(x.min())
    assert out.x.max() == pytest.approx(x.max())


def test_data_without_group_support_without_grid():
    x = np.random.uniform(size=20)
    stat = KDE(gridsize=None)
    data = pd.DataFrame({"x": x})
    gb = GroupBy([])
    scales = dict(x=Continuous())
    out = stat(data, gb, "x", scales)
    assert_array_equal(out.x, x)


def test_data_without_group_weighted_support_with_grid():
    x = np.random.uniform(size=20)
    w = np.random.uniform(size=20)
    stat = KDE(gridsize=10, cut=0)
    data = pd.DataFrame({"x": x, "weight": w})
    gb = GroupBy([])
    scales = dict(x=Continuous())
    out = stat(data, gb, "x", scales)
    assert out.x.min() == pytest.approx(x.min())
    assert out.x.max() == pytest.approx(x.max())


def test_data_without_group_weighted_support_without_grid():
    x = np.random.uniform(size=20)
    w = np.random.uniform(size=20)
    stat = KDE(gridsize=None)
    data = pd.DataFrame({"x": x, "weight": w})
    gb = GroupBy([])
    scales = dict(x=Continuous())
    out = stat(data, gb, "x", scales)
    assert_array_equal(out.x, x)


def test_kde_result():
    x = np.random.normal(size=200)
    stat = KDE()
    data = pd.DataFrame({"x": x})
    gb = GroupBy(["x"])
    scales = dict(x=Continuous())
    out = stat(data, gb, "x", scales)
    assert_frame_equal(out, stat(data, gb, "x", scales))


def test_kde_result_weighted():
    x = np.random.normal(size=200)
    w = np.random.uniform(size=200)
    stat = KDE()
    data = pd.DataFrame({"x": x, "weight": w})
    gb = GroupBy(["x"])
    scales = dict(x=Continuous())
    out = stat(data, gb, "x", scales)
    assert_frame_equal(out, stat(data, gb, "x", scales))


def test_kde_result_without_group():
    x = np.random.normal(size=200)
    stat = KDE()
    data = pd.DataFrame({"x": x})
    gb = GroupBy([])
    scales = dict(x=Continuous())
    out = stat(data, gb, "x", scales)
    assert_frame_equal(out, stat(data, gb, "x", scales))


def test_kde_result_without_group_weighted():
    x = np.random.normal(size=200)
    w = np.random.uniform(size=200)
    stat = KDE()
    data = pd.DataFrame({"x": x, "weight": w})
    gb = GroupBy([])
    scales = dict(x=Continuous())
    out = stat(data, gb, "x", scales)
    assert_frame_equal(out, stat(data, gb, "x", scales))


def test_kde_result_with_grid():
    x = np.random.normal(size=200)
    stat = KDE(gridsize=100)
    data = pd.DataFrame({"x": x})
    gb = GroupBy(["x"])
    scales = dict(x=Continuous())
    out = stat(data, gb, "x", scales)
    assert_frame_equal(out, stat(data, gb, "x", scales))


def test_kde_result_with_grid_weighted():
    x = np.random.normal(size=200)
    w = np.random.uniform(size=200)
    stat = KDE(gridsize=100)
    data = pd.DataFrame({"x": x, "weight": w})
    gb = GroupBy(["x"])
    scales = dict(x=Continuous())
    out = stat(data, gb, "x", scales)
    assert_frame_equal(out, stat(data, gb, "x", scales))


def test_kde_result_without_group_with_grid():
    x = np.random.normal(size=200)
    stat = KDE(gridsize=100)
    data = pd.DataFrame({"x": x})
    gb = GroupBy([])
    scales = dict(x=Continuous())
    out = stat(data, gb, "x", scales)
    assert_frame_equal(out, stat(data, gb, "x", scales))


def test_kde_result_without_group_with_grid_weighted():
    x = np.random.normal(size=200)
    w = np.random.uniform(size=200)
    stat = KDE(gridsize=100)
    data = pd.DataFrame({"x": x, "weight": w})
    gb = GroupBy([])
    scales = dict(x=Continuous())
    out = stat(data, gb, "x", scales)
    assert_frame_equal(out, stat(data, gb, "x", scales))


def test_kde_result_cumulative():
    x = np.random.normal(size=200)
    stat = KDE(cumulative=True)
    data = pd.DataFrame({"x": x})
    gb = GroupBy(["x"])
    scales = dict(x=Continuous())
    out = stat(data, gb, "x", scales)
    assert_frame_equal(out, stat(data, gb, "x", scales))


def test_kde_result_cumulative_weighted():
    x = np.random.normal(size=200)
    w = np.random.uniform(size=200)
    stat = KDE(cumulative=True)
    data = pd.DataFrame({"x": x, "weight": w})
    gb = GroupBy(["x"])
    scales = dict(x=Continuous())
    out = stat(data, gb, "x", scales)
    assert_frame_equal(out, stat(data, gb, "x", scales))


def test_kde_result_without_group_cumulative():
    x = np.random.normal(size=200)
    stat = KDE(cumulative=True)
    data = pd.DataFrame({"x": x})
    gb = GroupBy([])
    scales = dict(x=Continuous())
    out = stat(data, gb, "x", scales)
    assert_frame_equal(out, stat(data, gb, "x", scales))


def test_kde_result_without_group_cumulative_weighted():
    x = np.random.normal(size=200)
    w = np.random.uniform(size=200)
    stat = KDE(cumulative=True)
    data = pd.DataFrame({"x": x, "weight": w})
    gb = GroupBy([])
    scales = dict(x=Continuous())
    out = stat(data, gb, "x", scales)
    assert_frame_equal(out, stat(data, gb, "x", scales))


def test_kde_result_with_grid_cumulative():
    x = np.random.normal(size=200)
    stat = KDE(gridsize=100, cumulative=True)
    data = pd.DataFrame({"x": x})
    gb = GroupBy(["x"])
    scales = dict(x=Continuous())
    out = stat(data, gb, "x", scales)
    assert_frame_equal(out, stat(data, gb, "x", scales))


def test_kde_result_with_grid_cumulative_weighted():
    x = np.random.normal(size=200)
    w = np.random.uniform(size=200)
    stat = KDE(gridsize=100, cumulative=True)
    data = pd.DataFrame({"x": x, "weight": w})
    gb = GroupBy(["x"])
    scales = dict(x=Continuous())
    out = stat(data, gb, "x", scales)
    assert_frame_equal(out, stat(data, gb, "x", scales))


def test_kde_result_without_group_with_grid_cumulative():
    x = np.random.normal(size=200)
    stat = KDE(gridsize=100, cumulative=True)
    data = pd.DataFrame({"x": x})
    gb = GroupBy([])
    scales = dict(x=Continuous())
    out = stat(data, gb, "x", scales)
    assert_frame_equal(out, stat(data, gb, "x", scales))


def test_kde_result_without_group_with_grid_cumulative_weighted():
    x = np.random.normal(size=200)
    w = np.random.uniform(size=200)
    stat = KDE(gridsize=100, cumulative=True)
    data = pd.DataFrame({"x": x, "weight": w})
    gb = GroupBy([])
    scales = dict(x=Continuous())
    out = stat(data, gb, "x", scales)
    assert_frame_equal(out, stat(data, gb, "x", scales))


def test_kde_result_categorical():
    x = np.random.normal(size=200)
    y = np.random.choice(["a", "b", "c"], 200)
    stat = KDE()
    data = pd.DataFrame({"x": x, "y": y})
    gb = GroupBy(["x", "y"])
    scales = dict(x=Continuous(), y=Nominal())
    out = stat(data, gb, "x", scales)
    assert_frame_equal(out, stat(data, gb, "x", scales))


def test_kde_result_categorical_weighted():
    x = np.random.normal(size=200)
    y = np.random.choice(["a", "b", "c"], 200)
    w = np.random.uniform(size=200)
    stat = KDE()
    data = pd.DataFrame({"x": x, "y": y, "weight": w})
    gb = GroupBy(["x", "y"])
    scales = dict(x=Continuous(), y=Nominal())
    out = stat(data, gb, "x", scales)
    assert_frame_equal(out, stat(data, gb, "x", scales))


def test_kde_result_categorical_with_grid():
    x = np.random.normal(size=200)
    y = np.random.choice(["a", "b", "c"], 200)
    stat = KDE(gridsize=100)
    data = pd.DataFrame({"x": x, "y": y})
    gb = GroupBy(["x", "y"])
    scales = dict(x=Continuous(), y=Nominal())
    out = stat(data, gb, "x", scales)
    assert_frame_equal(out, stat(data, gb, "x", scales))


def test_kde_result_categorical_with_grid_weighted():
    x = np.random.normal(size=200)
    y = np.random.choice(["a", "b", "c"], 200)
    w = np.random.uniform(size=200)
    stat = KDE(gridsize=100)
    data = pd.DataFrame({"x": x, "y": y, "weight": w})
    gb = GroupBy(["x", "y"])
    scales = dict(x=Continuous(), y=Nominal())
    out = stat(data, gb, "x", scales)
    assert_frame_equal(out, stat(data, gb, "x", scales))


def test_kde_result_categorical_within_grid():
    x = np.random.normal(size=200)
    y = np.random.choice(["a", "b", "c"], 200)
    stat = KDE(gridsize=100, common_grid=["y"])
    data = pd.DataFrame({"x": x, "y": y})
    gb = GroupBy(["x", "y"])
    scales = dict(x=Continuous(), y=Nominal())
    out = stat(data, gb, "x", scales)
    assert_frame_equal(out, stat(data, gb, "x", scales))


def test_kde_result_categorical_within_grid_weighted():
    x = np.random.normal(size=200)
    y = np.random.choice(["a", "b", "c"], 200)
    w = np.random.uniform(size=200)
    stat = KDE(gridsize=100, common_grid=["y"])
    data = pd.DataFrame({"x": x, "y": y, "weight": w})
    gb = GroupBy(["x", "y"])
    scales = dict(x=Continuous(), y=Nominal())
    out = stat(data, gb, "x", scales)
    assert_frame_equal(out, stat(data, gb, "x", scales))


def test_kde_result_categorical_double():
    x = np.random.normal(size=200)
    y = np.random.choice(["a", "b", "c"], 200)
    z = np.random.choice(["A", "B", "C"], 200)
    stat = KDE()
    data = pd.DataFrame({"x": x, "y": y, "z": z})
    gb = GroupBy(["x", "y", "z"])
    scales = dict(x=Continuous(), y=Nominal(), z=Nominal())
    out = stat(data, gb, "x", scales)
    assert_frame_equal(out, stat(data, gb, "x", scales))


def test_kde_result_categorical_double_weighted():
    x = np.random.normal(size=200)
    y = np.random.choice(["a", "b", "c"], 200)
    z = np.random.choice(["A", "B", "C"], 200)
    w = np.random.uniform(size=200)
    stat = KDE()
    data = pd.DataFrame({"x": x, "y": y, "z": z, "weight": w})
    gb = GroupBy(["x", "y", "z"])
    scales = dict(x=Continuous(), y=Nominal(), z=Nominal())
    out = stat(data, gb, "x", scales)
    assert_frame_equal(out, stat(data, gb, "x", scales))


def test_kde_result_categorical_double_with_grid():
    x = np.random.normal(size=200)
    y = np.random.choice(["a", "b", "c"], 200)
    z = np.random.choice(["A", "B", "C"], 200)
    stat = KDE(gridsize=100)
    data = pd.DataFrame({"x": x, "y": y, "z": z})
    gb = GroupBy(["x", "y", "z"])
    scales = dict(x=Continuous(), y=Nominal(), z=Nominal())
    out = stat(data, gb, "x", scales)
    assert_frame_equal(out, stat(data, gb, "x", scales))


def test_kde_result_categorical_double_with_grid_weighted():
    x = np.random.normal(size=200)
    y = np.random.choice(["a", "b", "c"], 200)
    z = np.random.choice(["A", "B", "C"], 200)
    w = np.random.uniform(size=200)
    stat = KDE(gridsize=100)
    data = pd.DataFrame({"x": x, "y": y, "z": z, "weight": w})
    gb = GroupBy(["x", "y", "z"])
    scales = dict(x=Continuous(), y=Nominal(), z=Nominal())
    out = stat(data, gb, "x", scales)
    assert_frame_equal(out, stat(data, gb, "x", scales))


def test_kde_result_categorical_double_within_grid():
    x = np.random.normal(size=200)
    y = np.random.choice(["a", "b", "c"], 200