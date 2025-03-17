import pytest
import pandas as pd
import numpy as np
from seaborn._core.groupby import GroupBy
from seaborn._core.scales import Scale
from seaborn._stats.base import Stat
from seaborn._stats.base import Count, Hist

@pytest.fixture
def simple_dataframe():
    return pd.DataFrame({
        'x': [1, 2, 2, 3, 3, 3],
        'y': [1, 1, 2, 2, 3, 3]
    })

@pytest.fixture
def simple_groupby():
    order = ['x']
    return GroupBy(order)

@pytest.fixture
def simple_scales():
    return {'x': Scale(), 'y': Scale()}

def test_count_call(simple_dataframe, simple_groupby, simple_scales):
    count_stat = Count()
    result = count_stat(simple_dataframe, simple_groupby, 'x', simple_scales)
    expected = pd.DataFrame({
        'y': [2, 3, 1],
        'x': [1, 2, 3]
    })
    pd.testing.assert_frame_equal(result, expected)

def test_hist_call_count(simple_dataframe, simple_groupby, simple_scales):
    hist_stat = Hist(stat='count')
    result = hist_stat(simple_dataframe, simple_groupby, 'x', simple_scales)
    expected = pd.DataFrame({
        'x': [1.5, 2.5, 3.5],
        'count': [1, 2, 3],
        'space': [1, 1, 1],
        'y': [1, 2, 3]
    })
    pd.testing.assert_frame_equal(result, expected)

def test_hist_call_density(simple_dataframe, simple_groupby, simple_scales):
    hist_stat = Hist(stat='density')
    result = hist_stat(simple_dataframe, simple_groupby, 'x', simple_scales)
    expected = pd.DataFrame({
        'x': [1.5, 2.5, 3.5],
        'count': [1/6, 2/6, 3/6],
        'space': [1, 1, 1],
        'y': [1/6, 2/6, 3/6]
    })
    pd.testing.assert_frame_equal(result, expected)

def test_hist_call_percent(simple_dataframe, simple_groupby, simple_scales):
    hist_stat = Hist(stat='percent')
    result = hist_stat(simple_dataframe, simple_groupby, 'x', simple_scales)
    expected = pd.DataFrame({
        'x': [1.5, 2.5, 3.5],
        'count': [100/6, 200/6, 300/6],
        'space': [1, 1, 1],
        'y': [100/6, 200/6, 300/6]
    })
    pd.testing.assert_frame_equal(result, expected)

def test_hist_call_proportion(simple_dataframe, simple_groupby, simple_scales):
    hist_stat = Hist(stat='proportion')
    result = hist_stat(simple_dataframe, simple_groupby, 'x', simple_scales)
    expected = pd.DataFrame({
        'x': [1.5, 2.5, 3.5],
        'count': [1/6, 2/6, 3/6],
        'space': [1, 1, 1],
        'y': [1/6, 2/6, 3/6]
    })
    pd.testing.assert_frame_equal(result, expected)

def test_hist_call_frequency(simple_dataframe, simple_groupby, simple_scales):
    hist_stat = Hist(stat='frequency')
    result = hist_stat(simple_dataframe, simple_groupby, 'x', simple_scales)
    expected = pd.DataFrame({
        'x': [1.5, 2.5, 3.5],
        'count': [1, 2, 3],
        'space': [1, 1, 1],
        'y': [1, 2, 3]
    })
    pd.testing.assert_frame_equal(result, expected)

def test_hist_invalid_stat():
    with pytest.raises(ValueError):
        Hist(stat='invalid_stat')