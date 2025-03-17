import pytest
import pandas as pd
from seaborn._core.groupby import GroupBy
from seaborn._core.scales import Scale
from seaborn.test_aggregation import Agg, Est

@pytest.fixture
def data():
    return pd.DataFrame({
        "x": [1, 2, 3, 4, 5],
        "y": [2, 3, 4, 5, 6],
        "weight": [1, 0.5, 0.5, 1, 1]
    })

@pytest.fixture
def groupby():
    return GroupBy(order=["x"])

@pytest.fixture
def scales():
    return {"x": Scale(), "y": Scale()}

def test_agg_mean(data, groupby, scales):
    agg = Agg(func="mean")
    result = agg(data, groupby, "x", scales)
    assert "y" in result
    assert result["y"].iloc[0] == data["y"].mean()

def test_agg_custom_function(data, groupby, scales):
    agg = Agg(func=lambda x: x.max() - x.min())
    result = agg(data, groupby, "x", scales)
    assert "y" in result
    assert result["y"].iloc[0] == data["y"].max() - data["y"].min()

def test_est_mean_ci(data, groupby, scales):
    est = Est(func="mean", errorbar=("ci", 95))
    result = est(data, groupby, "x", scales)
    assert "y" in result
    assert "ymin" in result
    assert "ymax" in result

def test_est_weighted_mean_ci(data, groupby, scales):
    est = Est(func="mean", errorbar=("ci", 95))
    result = est(data, groupby, "x", scales)
    assert "y" in result
    assert "ymin" in result
    assert "ymax" in result

def test_est_custom_errorbar_function(data, groupby, scales):
    def custom_errorbar(x):
        return x.min(), x.max()

    est = Est(func="mean", errorbar=custom_errorbar)
    result = est(data, groupby, "x", scales)
    assert "y" in result
    assert "ymin" in result
    assert "ymax" in result
    assert result["ymin"].iloc[0] == data["y"].min()
    assert result["ymax"].iloc[0] == data["y"].max()

def test_agg_invalid_function(data, groupby, scales):
    with pytest.raises(AttributeError):
        agg = Agg(func="non_existent_function")
        agg(data, groupby, "x", scales)

def test_est_invalid_errorbar_method(data, groupby, scales):
    with pytest.raises(ValueError):
        Est(func="mean", errorbar=("invalid_method", 95))