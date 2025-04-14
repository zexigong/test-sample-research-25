import numpy as np
import pytest

from seaborn.algorithms import bootstrap


def test_bootstrap_seed():
    """Test that bootstrap returns the same thing with the same seed."""
    x = np.random.normal(size=50)

    seed = 0
    out1 = bootstrap(x, seed=seed)
    out2 = bootstrap(x, seed=seed)
    assert np.array_equal(out1, out2)

    rng = np.random.default_rng(seed)
    out3 = bootstrap(x, seed=rng)
    assert np.array_equal(out1, out3)

    ss = np.random.SeedSequence(seed)
    out4 = bootstrap(x, seed=ss)
    assert np.array_equal(out1, out4)

    rs = np.random.RandomState(seed)
    out5 = bootstrap(x, seed=rs)
    assert np.array_equal(out1, out5)


def test_bootstrap_random_seed():
    """Test that bootstrap returns the same thing with the same random_seed."""
    x = np.random.normal(size=50)

    seed = 0
    out1 = bootstrap(x, random_seed=seed)
    out2 = bootstrap(x, random_seed=seed)
    assert np.array_equal(out1, out2)

    rng = np.random.default_rng(seed)
    out3 = bootstrap(x, random_seed=rng)
    assert np.array_equal(out1, out3)

    ss = np.random.SeedSequence(seed)
    out4 = bootstrap(x, random_seed=ss)
    assert np.array_equal(out1, out4)

    rs = np.random.RandomState(seed)
    out5 = bootstrap(x, random_seed=rs)
    assert np.array_equal(out1, out5)


def test_bootstrap_units():
    """Test that the units argument has the intended effect."""
    x = np.random.normal(size=50)
    y = np.random.normal(size=50)
    units = np.repeat(np.arange(10), 5)

    seed = 0
    out1 = bootstrap(x, y, seed=seed)
    out2 = bootstrap(x, y, units=units, seed=seed)
    assert not np.array_equal(out1, out2)


def test_bootstrap_axis():
    """Test the axis argument."""
    x = np.random.normal(size=(50, 2))

    seed = 0
    out1 = bootstrap(x, seed=seed)
    out2 = bootstrap(x, axis=0, seed=seed)
    assert np.array_equal(out1, out2)

    out3 = bootstrap(x, axis=1, seed=seed)
    assert not np.array_equal(out1, out3)

    out4 = bootstrap(x.T, seed=seed)
    assert np.array_equal(out3, out4.T)


def test_bootstrap_func():
    """Test the func argument."""
    x = np.random.normal(size=50)

    seed = 0
    out1 = bootstrap(x, func="mean", seed=seed)
    out2 = bootstrap(x, seed=seed)
    assert np.array_equal(out1, out2)

    out3 = bootstrap(x, func=np.mean, seed=seed)
    assert np.array_equal(out1, out3)

    out4 = bootstrap(x, func=np.std, seed=seed)
    assert not np.array_equal(out1, out4)


def test_bootstrap_missing():
    """Test the func argument."""
    x = np.random.normal(size=50)
    x[10] = np.nan

    seed = 0
    out1 = bootstrap(x, func="mean", seed=seed)
    out2 = bootstrap(x, func="nanmean", seed=seed)
    assert np.array_equal(out1, out2)

    out3 = bootstrap(x, func=np.mean, seed=seed)
    assert np.array_equal(out1, out3)

    out4 = bootstrap(x, func=np.nanmean, seed=seed)
    assert np.array_equal(out1, out4)

    out5 = bootstrap(x, func=np.std, seed=seed)
    assert not np.array_equal(out1, out5)


def test_bootstrap_mismatch_raises():
    """Test that bootstrap raises on unequal length inputs."""
    x = np.random.normal(size=50)
    y = np.random.normal(size=51)
    with pytest.raises(ValueError):
        bootstrap(x, y)