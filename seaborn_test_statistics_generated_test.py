import numpy as np
import pandas as pd
import pytest

from seaborn import _statistics as stats


class TestKDE:

    def test_univariate(self):

        x = np.random.RandomState(0).normal(size=100)
        kde = stats.KDE(gridsize=1000)
        density, support = kde(x)
        assert density.size == support.size == 1000

    def test_bivariate(self):

        x = np.random.RandomState(0).normal(size=(100, 2))
        kde = stats.KDE(gridsize=100)
        density, support = kde(*x.T)
        assert density.shape == (100, 100)
        assert len(support) == 2
        assert support[0].size == support[1].size == 100

    def test_univariate_cumulative(self):

        x = np.random.RandomState(0).normal(size=100)
        kde = stats.KDE(gridsize=1000, cumulative=True)
        density, support = kde(x)
        assert density.size == support.size == 1000
        assert np.isclose(density.min(), 0)
        assert np.isclose(density.max(), 1)

    def test_bivariate_cumulative(self):

        x = np.random.RandomState(0).normal(size=(100, 2))
        kde = stats.KDE(gridsize=100, cumulative=True)
        density, support = kde(*x.T)
        assert density.shape == (100, 100)
        assert len(support) == 2
        assert support[0].size == support[1].size == 100
        assert np.isclose(density.min(), 0)
        assert np.isclose(density.max(), 1)


class TestHistogram:

    def test_univariate(self):

        x = np.random.RandomState(0).normal(size=100)
        hist = stats.Histogram()
        density, support = hist(x)
        assert density.size == support.size - 1

    def test_bivariate(self):

        x = np.random.RandomState(0).normal(size=(100, 2))
        hist = stats.Histogram()
        density, support = hist(*x.T)
        assert density.shape == (support[0].size - 1, support[1].size - 1)


class TestECDF:

    def test_univariate(self):

        x = np.random.RandomState(0).normal(size=100)
        stat = stats.ECDF()
        density, support = stat(x)
        assert density.size == support.size

    def test_complementary(self):

        x = np.random.RandomState(0).normal(size=100)
        stat = stats.ECDF(complementary=True)
        density, support = stat(x)
        assert density.size == support.size
        assert np.all(np.diff(density) <= 0)


class TestEstimateAggregator:

    def test_default(self):

        data = pd.DataFrame({"x": [1, 2, 3, 4, 5]})
        stat = stats.EstimateAggregator(estimator="mean")
        out = stat(data, "x")
        assert out["x"] == 3
        assert np.isnan(out["xmin"])
        assert np.isnan(out["xmax"])

    def test_ci(self):

        data = pd.DataFrame({"x": [1, 2, 3, 4, 5]})
        stat = stats.EstimateAggregator(estimator="mean", errorbar=("ci", 100))
        out = stat(data, "x")
        assert out["x"] == 3
        assert np.isclose(out["xmin"], 1)
        assert np.isclose(out["xmax"], 5)

    def test_sd(self):

        data = pd.DataFrame({"x": [1, 2, 3, 4, 5]})
        stat = stats.EstimateAggregator(estimator="mean", errorbar=("sd", 1))
        out = stat(data, "x")
        assert out["x"] == 3
        assert np.isclose(out["xmin"], 3 - data["x"].std())
        assert np.isclose(out["xmax"], 3 + data["x"].std())

    def test_se(self):

        data = pd.DataFrame({"x": [1, 2, 3, 4, 5]})
        stat = stats.EstimateAggregator(estimator="mean", errorbar=("se", 1))
        out = stat(data, "x")
        assert out["x"] == 3
        assert np.isclose(out["xmin"], 3 - data["x"].sem())
        assert np.isclose(out["xmax"], 3 + data["x"].sem())

    def test_pi(self):

        data = pd.DataFrame({"x": [1, 2, 3, 4, 5]})
        stat = stats.EstimateAggregator(estimator="mean", errorbar=("pi", 100))
        out = stat(data, "x")
        assert out["x"] == 3
        assert np.isclose(out["xmin"], 1)
        assert np.isclose(out["xmax"], 5)

    def test_error_func(self):

        data = pd.DataFrame({"x": [1, 2, 3, 4, 5]})
        stat = stats.EstimateAggregator(
            estimator="mean", errorbar=lambda x: (x.min(), x.max())
        )
        out = stat(data, "x")
        assert out["x"] == 3
        assert np.isclose(out["xmin"], 1)
        assert np.isclose(out["xmax"], 5)


class TestWeightedAggregator:

    def test_mean(self):

        data = pd.DataFrame({"x": [1, 2, 3, 4, 5], "weight": [1, 1, 1, 1, 1]})
        stat = stats.WeightedAggregator(estimator="mean")
        out = stat(data, "x")
        assert out["x"] == 3
        assert np.isnan(out["xmin"])
        assert np.isnan(out["xmax"])

    def test_mean_ci(self):

        data = pd.DataFrame({"x": [1, 2, 3, 4, 5], "weight": [1, 1, 1, 1, 1]})
        stat = stats.WeightedAggregator(estimator="mean", errorbar=("ci", 100))
        out = stat(data, "x")
        assert out["x"] == 3
        assert np.isclose(out["xmin"], 1)
        assert np.isclose(out["xmax"], 5)


class TestLetterValues:

    def test_proportion(self):

        x = np.random.RandomState(0).normal(size=100)
        lv = stats.LetterValues("proportion", 0.1, 0.05)
        out = lv(x)
        assert out["k"] == 6
        assert np.all(out["percs"] == np.array([
            0.78125, 0.859375, 0.90625, 0.9375, 0.9609375, 0.9765625, 0.984375,
            0.9921875, 0.99609375, 0.99804688, 0.99902344, 0.99951172, 1.,
        ]) * 100)

    def test_trustworthy(self):

        x = np.random.RandomState(0).normal(size=100)
        lv = stats.LetterValues("trustworthy", 0.1, 0.05)
        out = lv(x)
        assert out["k"] == 4
        assert np.all(out["percs"] == np.array([
            0.5, 0.75, 0.875, 0.9375, 0.96875, 0.984375, 0.9921875, 0.99609375,
            0.99804688, 0.99902344, 0.99951172, 1.,
        ]) * 100)

    def test_tukey(self):

        x = np.random.RandomState(0).normal(size=100)
        lv = stats.LetterValues("tukey", 0.1, 0.05)
        out = lv(x)
        assert out["k"] == 4
        assert np.all(out["percs"] == np.array([
            0.5, 0.75, 0.875, 0.9375, 0.96875, 0.984375, 0.9921875, 0.99609375,
            0.99804688, 0.99902344, 0.99951172, 1.,
        ]) * 100)

    def test_full(self):

        x = np.random.RandomState(0).normal(size=100)
        lv = stats.LetterValues("full", 0.1, 0.05)
        out = lv(x)
        assert out["k"] == 7
        assert np.all(out["percs"] == np.array([
            0.5, 0.75, 0.875, 0.9375, 0.96875, 0.984375, 0.9921875, 0.99609375,
            0.99804688, 0.99902344, 0.99951172, 1.,
        ]) * 100)

    def test_explicit(self):

        x = np.random.RandomState(0).normal(size=100)
        lv = stats.LetterValues(3, 0.1, 0.05)
        out = lv(x)
        assert out["k"] == 3
        assert np.all(out["percs"] == np.array([
            0.5, 0.75, 0.875, 0.9375, 0.96875, 0.984375, 0.9921875, 0.99609375,
            0.99804688, 0.99902344, 0.99951172, 1.,
        ]) * 100)


def test_validate_errorbar_arg():

    assert stats._validate_errorbar_arg(None) == (None, None)
    assert stats._validate_errorbar_arg("ci") == ("ci", 95)
    assert stats._validate_errorbar_arg(("ci", 90)) == ("ci", 90)
    assert stats._validate_errorbar_arg(("pi", 90)) == ("pi", 90)
    assert stats._validate_errorbar_arg(("sd", 2)) == ("sd", 2)
    assert stats._validate_errorbar_arg(("se", 2)) == ("se", 2)
    assert stats._validate_errorbar_arg(lambda x: (0, 1)) == (lambda x: (0, 1), None)

    with pytest.raises(ValueError):
        stats._validate_errorbar_arg("xx")

    with pytest.raises(TypeError):
        stats._validate_errorbar_arg("ci", "sd")

    with pytest.raises(TypeError):
        stats._validate_errorbar_arg((90, "ci"))

    with pytest.raises(TypeError):
        stats._validate_errorbar_arg((90, 90))