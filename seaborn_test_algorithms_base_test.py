import numpy as np
import pytest
from seaborn.algorithms import bootstrap

def test_bootstrap_basic_mean():
    data = np.array([1, 2, 3, 4, 5])
    result = bootstrap(data, n_boot=1000, func="mean", seed=0)
    assert result.shape == (1000,)
    assert np.isclose(result.mean(), np.mean(data), atol=0.1)

def test_bootstrap_basic_sum():
    data = np.array([1, 2, 3, 4, 5])
    result = bootstrap(data, n_boot=1000, func="sum", seed=0)
    assert result.shape == (1000,)
    assert np.isclose(result.mean(), np.sum(data), atol=0.1)

def test_bootstrap_with_units():
    data = np.array([1, 2, 3, 4, 5, 6])
    units = np.array([0, 0, 1, 1, 2, 2])
    result = bootstrap(data, units=units, n_boot=1000, func="mean", seed=0)
    assert result.shape == (1000,)
    assert np.isclose(result.mean(), np.mean(data), atol=0.1)

def test_bootstrap_func_callable():
    data = np.array([1, 2, 3, 4, 5])
    result = bootstrap(data, n_boot=1000, func=np.median, seed=0)
    assert result.shape == (1000,)
    assert np.isclose(result.mean(), np.median(data), atol=0.1)

def test_bootstrap_raises_on_mismatched_lengths():
    data1 = np.array([1, 2, 3])
    data2 = np.array([4, 5])
    with pytest.raises(ValueError, match="All input arrays must have the same length"):
        bootstrap(data1, data2, n_boot=1000, func="mean", seed=0)

def test_bootstrap_with_nan_data():
    data = np.array([1, 2, np.nan, 4, 5])
    result = bootstrap(data, n_boot=1000, func="mean", seed=0)
    assert result.shape == (1000,)
    assert np.all(np.isfinite(result))

def test_bootstrap_warning_for_random_seed():
    data = np.array([1, 2, 3, 4, 5])
    with pytest.warns(UserWarning, match="`random_seed` has been renamed to `seed` and will be removed"):
        bootstrap(data, n_boot=1000, func="mean", random_seed=0)

def test_bootstrap_unsupported_nan_func_warning():
    data = np.array([1, 2, np.nan, 4, 5])
    with pytest.warns(UserWarning, match="Data contain nans but no nan-aware version of `sum` found"):
        bootstrap(data, n_boot=1000, func="sum", seed=0)

def test_bootstrap_with_axis():
    data = np.array([[1, 2, 3], [4, 5, 6]])
    result = bootstrap(data, n_boot=1000, func="mean", axis=0, seed=0)
    assert result.shape == (1000, 3)
    assert np.allclose(result.mean(axis=0), np.mean(data, axis=0), atol=0.1)