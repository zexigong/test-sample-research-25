import pytest
import numpy as np
import pandas as pd
from seaborn._stats.base import Stat
from seaborn._core.groupby import GroupBy
from seaborn._core.scales import Scale
from seaborn.test_density.test_density import KDE

def test_kde_initialization():
    kde = KDE()
    assert kde.bw_adjust == 1
    assert kde.bw_method == "scott"
    assert kde.common_norm is True
    assert kde.common_grid is True
    assert kde.gridsize == 200
    assert kde.cut == 3
    assert kde.cumulative is False

def test_kde_post_init_no_scipy():
    kde = KDE(cumulative=True)
    if kde._no_scipy:
        with pytest.raises(RuntimeError):
            kde.__post_init__()

def test_kde_check_var_list_or_boolean():
    kde = KDE()
    kde._check_var_list_or_boolean("common_grid", [])
    kde._check_var_list_or_boolean("common_norm", [])
    with pytest.raises(TypeError):
        kde.common_grid = "invalid"
        kde._check_var_list_or_boolean("common_grid", [])

def test_kde_fit():
    kde = KDE()
    data = pd.DataFrame({"x": np.random.randn(100)})
    result = kde._fit(data, "x")
    assert isinstance(result, kde.gaussian_kde)

def test_kde_get_support():
    kde = KDE()
    data = pd.DataFrame({"x": np.random.randn(100)})
    result = kde._get_support(data, "x")
    assert isinstance(result, np.ndarray)
    assert len(result) == kde.gridsize

def test_kde_fit_and_evaluate():
    kde = KDE()
    data = pd.DataFrame({"x": np.random.randn(100)})
    support = kde._get_support(data, "x")
    result = kde._fit_and_evaluate(data, "x", support)
    assert isinstance(result, pd.DataFrame)
    assert "density" in result.columns

def test_kde_transform():
    kde = KDE()
    data = pd.DataFrame({"x": np.random.randn(100)})
    result = kde._transform(data, "x", [])
    assert isinstance(result, pd.DataFrame)
    assert "density" in result.columns

def test_kde_call():
    kde = KDE()
    data = pd.DataFrame({"x": np.random.randn(100)})
    groupby = GroupBy(["x"])
    scales = {"x": Scale()}
    result = kde(data, groupby, "x", scales)
    assert isinstance(result, pd.DataFrame)
    assert "density" in result.columns

@pytest.mark.parametrize("bw_adjust", [0.5, 1, 2])
def test_kde_bw_adjust(bw_adjust):
    kde = KDE(bw_adjust=bw_adjust)
    data = pd.DataFrame({"x": np.random.randn(100)})
    kde._fit(data, "x")
    assert kde.bw_adjust == bw_adjust