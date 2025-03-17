import pytest
import pandas as pd
import numpy as np
from seaborn._stats.base import Stat
from seaborn.test_regression.test_regression import PolyFit

@pytest.fixture
def sample_data():
    return pd.DataFrame({
        "x": np.arange(10),
        "y": np.random.rand(10)
    })

@pytest.fixture
def insufficient_data():
    return pd.DataFrame({
        "x": np.arange(2),
        "y": np.random.rand(2)
    })

@pytest.fixture
def groupby():
    class DummyGroupBy:
        def apply(self, data, func):
            return func(data)

    return DummyGroupBy()

@pytest.fixture
def scales():
    return {}

def test_polyfit_fit_predict(sample_data):
    polyfit = PolyFit(order=2, gridsize=100)
    result = polyfit._fit_predict(sample_data)

    assert isinstance(result, pd.DataFrame)
    assert "x" in result.columns
    assert "y" in result.columns
    assert len(result) == polyfit.gridsize

def test_polyfit_fit_predict_insufficient_data(insufficient_data):
    polyfit = PolyFit(order=2, gridsize=100)
    result = polyfit._fit_predict(insufficient_data)

    assert isinstance(result, pd.DataFrame)
    assert result.empty

def test_polyfit_call(sample_data, groupby, scales):
    polyfit = PolyFit(order=2, gridsize=100)
    result = polyfit(sample_data, groupby, orient="x", scales=scales)

    assert isinstance(result, pd.DataFrame)
    assert "x" in result.columns
    assert "y" in result.columns