"""Tests for algorithms to support fitting routines in seaborn plotting functions."""
import numpy as np
import pytest

from seaborn._algorithms import bootstrap


class TestBootstrap:

    def test_bootstrap_dist_length(self):

        x = np.random.normal(size=100)
        dist = bootstrap(x, n_boot=100)
        assert len(dist) == 100

    def test_bootstrap_dist_length_with_units(self):

        x = np.random.normal(size=100)
        units = np.repeat(np.arange(10), 10)
        dist = bootstrap(x, n_boot=100, units=units)
        assert len(dist) == 100

    def test_bootstrap_dist_length_with_axis(self):

        x = np.random.normal(size=(10, 10))
        dist = bootstrap(x, n_boot=100, axis=1)
        assert len(dist) == 100

    def test_bootstrap_dist_length_with_units_and_axis(self):

        x = np.random.normal(size=(10, 10))
        units = np.repeat(np.arange(10), 1)
        dist = bootstrap(x, n_boot=100, units=units, axis=1)
        assert len(dist) == 100

    def test_bootstrap_dist_shape(self):

        x = np.random.normal(size=(10, 10))
        dist = bootstrap(x, n_boot=100, axis=1)
        assert dist.shape == (100, 10)

    def test_bootstrap_dist_shape_with_units(self):

        x = np.random.normal(size=(10, 10))
        units = np.repeat(np.arange(10), 1)
        dist = bootstrap(x, n_boot=100, units=units, axis=1)
        assert dist.shape == (100, 10)

    def test_bootstrap_dist_shape_with_multiarg(self):

        x = np.random.normal(size=10)
        y = np.random.normal(size=10)
        dist = bootstrap(x, y, n_boot=100)
        assert dist.shape == (100, )

    def test_bootstrap_dist_shape_with_multiarg_and_units(self):

        x = np.random.normal(size=10)
        y = np.random.normal(size=10)
        units = np.repeat(np.arange(10), 1)
        dist = bootstrap(x, y, n_boot=100, units=units)
        assert dist.shape == (100, )

    def test_bootstrap_dist_shape_with_multiarg_and_axis(self):

        x = np.random.normal(size=(10, 2))
        y = np.random.normal(size=(10, 2))
        dist = bootstrap(x, y, n_boot=100, axis=1)
        assert dist.shape == (100, 2)

    def test_bootstrap_dist_shape_with_multiarg_and_units_and_axis(self):

        x = np.random.normal(size=(10, 2))
        y = np.random.normal(size=(10, 2))
        units = np.repeat(np.arange(10), 1)
        dist = bootstrap(x, y, n_boot=100, units=units, axis=1)
        assert dist.shape == (100, 2)

    def test_bootstrap_uses_nanfunc(self):

        x = np.random.normal(size=10)
        x[0] = np.nan
        dist = bootstrap(x, n_boot=10)
        assert not np.isnan(dist).any()

    def test_bootstrap_warns_with_nanfunc(self):

        x = np.random.normal(size=10)
        x[0] = np.nan
        with pytest.warns(UserWarning):
            bootstrap(x, n_boot=10, func="std")

    def test_bootstrap_warns_with_no_nanfunc(self):

        x = np.random.normal(size=10)
        x[0] = np.nan
        with pytest.warns(UserWarning):
            bootstrap(x, n_boot=10, func="foo")

    def test_bootstrap_custom_func(self):

        x = np.random.normal(size=10)
        dist = bootstrap(x, n_boot=10, func=len)
        assert np.array_equal(dist, np.ones(10) * len(x))

    def test_bootstrap_custom_func_with_kwargs(self):

        x = np.random.normal(size=(10, 20))
        dist = bootstrap(x, n_boot=10, func=np.sum, axis=1)
        assert dist.shape == (10, )