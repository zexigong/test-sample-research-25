import pytest
import pandas as pd
from seaborn.test_groupby.test_groupby import GroupBy

@pytest.fixture
def sample_dataframe():
    return pd.DataFrame({
        "A": ["foo", "bar", "foo", "bar"],
        "B": ["one", "one", "two", "two"],
        "C": [1, 2, 3, 4],
        "D": [5, 6, 7, 8],
    })

def test_groupby_init_empty_order():
    with pytest.raises(ValueError, match="GroupBy requires at least one grouping variable"):
        GroupBy([])

def test_groupby_init_list_order():
    gb = GroupBy(["A", "B"])
    assert gb.order == {"A": None, "B": None}

def test_groupby_init_dict_order():
    gb = GroupBy({"A": ["foo", "bar"], "B": None})
    assert gb.order == {"A": ["foo", "bar"], "B": None}

def test_get_groups_no_levels(sample_dataframe):
    gb = GroupBy(["E"])
    grouper, groups = gb._get_groups(sample_dataframe)
    assert grouper == []
    assert groups.empty

def test_get_groups_single_level(sample_dataframe):
    gb = GroupBy({"A": ["foo", "bar"]})
    grouper, groups = gb._get_groups(sample_dataframe)
    assert grouper == "A"
    assert list(groups) == ["foo", "bar"]

def test_get_groups_multi_level(sample_dataframe):
    gb = GroupBy({"A": ["foo", "bar"], "B": ["one", "two"]})
    grouper, groups = gb._get_groups(sample_dataframe)
    assert grouper == ["A", "B"]
    assert list(groups) == [("foo", "one"), ("foo", "two"), ("bar", "one"), ("bar", "two")]

def test_agg_no_grouping_vars(sample_dataframe):
    gb = GroupBy({})
    with pytest.raises(ValueError, match="No grouping variables are present in dataframe"):
        gb.agg(sample_dataframe, {"C": "sum"})

def test_agg_with_groups(sample_dataframe):
    gb = GroupBy({"A": ["foo", "bar"]})
    result = gb.agg(sample_dataframe, C=("C", "sum"))
    expected = pd.DataFrame({"A": ["foo", "bar"], "C": [4, 6]})
    pd.testing.assert_frame_equal(result, expected)

def test_apply_no_grouping_vars(sample_dataframe):
    gb = GroupBy({})
    result = gb.apply(sample_dataframe, lambda df: df.assign(E=df["C"] + df["D"]))
    expected = sample_dataframe.assign(E=sample_dataframe["C"] + sample_dataframe["D"])
    pd.testing.assert_frame_equal(result, expected)

def test_apply_with_groups(sample_dataframe):
    gb = GroupBy({"A": ["foo", "bar"]})
    result = gb.apply(sample_dataframe, lambda df: df.assign(E=df["C"] * 2))
    expected = pd.DataFrame({
        "A": ["foo", "foo", "bar", "bar"],
        "B": ["one", "two", "one", "two"],
        "C": [1, 3, 2, 4],
        "D": [5, 7, 6, 8],
        "E": [2, 6, 4, 8],
    })
    pd.testing.assert_frame_equal(result, expected)