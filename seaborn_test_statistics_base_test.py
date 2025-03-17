import pytest
import numpy as np
import pandas as pd
from seaborn.test_statistics.test_statistics import KDE, Histogram, ECDF, EstimateAggregator, WeightedAggregator, LetterValues

@pytest.fixture
def sample_data():
    np.random.seed(0)
    x1 = np.random.normal(size=100)
    x2 = np.random.normal(size=100)
    weights = np.random.rand(100)
    return x1, x2, weights

def test_kde_univariate(sample_data):
    x1, _, weights = sample_data
    kde = KDE()
    density, support = kde(x1, weights=weights)
    assert isinstance(density, np.ndarray)
    assert isinstance(support, np.ndarray)
    assert len(density) == len(support)

def test_kde_bivariate(sample_data):
    x1, x2, weights = sample_data
    kde = KDE()
    density, support = kde(x1, x2, weights=weights)
    assert isinstance(density, np.ndarray)
    assert isinstance(support, tuple)
    assert len(support) == 2

def test_histogram_univariate(sample_data):
    x1, _, weights = sample_data
    hist = Histogram()
    count, bin_edges = hist(x1, weights=weights)
    assert isinstance(count, np.ndarray)
    assert isinstance(bin_edges, np.ndarray)

def test_histogram_bivariate(sample_data):
    x1, x2, weights = sample_data
    hist = Histogram()
    count, bin_edges = hist(x1, x2, weights=weights)
    assert isinstance(count, np.ndarray)
    assert isinstance(bin_edges, list)
    assert len(bin_edges) == 2

def test_ecdf_univariate(sample_data):
    x1, _, weights = sample_data
    ecdf = ECDF()
    y, x = ecdf(x1, weights=weights)
    assert isinstance(y, np.ndarray)
    assert isinstance(x, np.ndarray)

def test_estimate_aggregator(sample_data):
    x1, _, _ = sample_data
    data = pd.DataFrame({'var': x1})
    aggregator = EstimateAggregator(estimator='mean')
    result = aggregator(data, 'var')
    assert isinstance(result, pd.Series)
    assert 'var' in result
    assert 'varmin' in result
    assert 'varmax' in result

def test_weighted_aggregator(sample_data):
    x1, _, weights = sample_data
    data = pd.DataFrame({'var': x1, 'weight': weights})
    aggregator = WeightedAggregator(estimator='mean')
    result = aggregator(data, 'var')
    assert isinstance(result, pd.Series)
    assert 'var' in result
    assert 'varmin' in result
    assert 'varmax' in result

def test_letter_values(sample_data):
    x1, _, _ = sample_data
    lv = LetterValues(k_depth='tukey', outlier_prop=0.1, trust_alpha=0.05)
    result = lv(x1)
    assert isinstance(result, dict)
    assert 'k' in result
    assert 'levels' in result
    assert 'percs' in result
    assert 'values' in result
    assert 'fliers' in result
    assert 'median' in result