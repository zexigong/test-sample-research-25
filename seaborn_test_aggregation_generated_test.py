import numpy as np
import pandas as pd
import pytest

from seaborn._core.groupby import GroupBy
from seaborn._stats.base import Stat
from seaborn._statistics import EstimateAggregator
from seaborn._stats.aggregation import Agg, Est
from seaborn._core.typing import default


class TestAgg:

    def test_agg_mean(self):

        data = pd.DataFrame(dict(x=[1, 1, 2, 2], y=[1, 2, 1, 2]))
        groupby = GroupBy(["x"])

        stat = Agg("mean")
        result = stat(data, groupby, "x", {})

        expected = pd.DataFrame(dict(x=[1, 2], y=[1.5, 1.5]))
        assert result.equals(expected)

    def test_agg_median(self):

        data = pd.DataFrame(dict(x=[1, 1, 2, 2], y=[1, 2, 1, 2]))
        groupby = GroupBy(["x"])

        stat = Agg("median")
        result = stat(data, groupby, "x", {})

        expected = pd.DataFrame(dict(x=[1, 2], y=[1.5, 1.5]))
        assert result.equals(expected)

    def test_agg_custom_func(self):

        data = pd.DataFrame(dict(x=[1, 1, 2, 2], y=[1, 2, 1, 2]))
        groupby = GroupBy(["x"])

        stat = Agg(lambda x: x.median() - 1)
        result = stat(data, groupby, "x", {})

        expected = pd.DataFrame(dict(x=[1, 2], y=[.5, .5]))
        assert result.equals(expected)

    def test_agg_missing(self):

        data = pd.DataFrame(dict(x=[1, 1, 2, 2], y=[1, 2, np.nan, 2]))
        groupby = GroupBy(["x"])

        stat = Agg("mean")
        result = stat(data, groupby, "x", {})

        expected = pd.DataFrame(dict(x=[1, 2], y=[1.5, 2]))
        assert result.equals(expected)


class TestEst:

    def test_ci(self):

        stat = Est()
        groupby = GroupBy(["x"])

        data = pd.DataFrame(dict(x=[1, 1, 2, 2, 2], y=[3, 5, 2, 5, 7]))
        result = stat(data, groupby, "x", {})

        assert result.x.equals(pd.Series([1, 2], name="x"))
        assert np.allclose(result.y, [4, 4.66666667], atol=.1)
        assert np.allclose(result.ylow, [2.897, 2.077], atol=.1)
        assert np.allclose(result.yhigh, [5.103, 7.256], atol=.1)

    def test_ci_custom_func(self):

        stat = Est(errorbar="ci")
        groupby = GroupBy(["x"])

        data = pd.DataFrame(dict(x=[1, 1, 2, 2, 2], y=[3, 5, 2, 5, 7]))
        result = stat(data, groupby, "x", {})

        assert result.x.equals(pd.Series([1, 2], name="x"))
        assert np.allclose(result.y, [4, 4.66666667], atol=.1)
        assert np.allclose(result.ylow, [2.897, 2.077], atol=.1)
        assert np.allclose(result.yhigh, [5.103, 7.256], atol=.1)

    def test_ci_custom_func_level(self):

        stat = Est(errorbar=("ci", 50))
        groupby = GroupBy(["x"])

        data = pd.DataFrame(dict(x=[1, 1, 2, 2, 2], y=[3, 5, 2, 5, 7]))
        result = stat(data, groupby, "x", {})

        assert result.x.equals(pd.Series([1, 2], name="x"))
        assert np.allclose(result.y, [4, 4.66666667], atol=.1)
        assert np.allclose(result.ylow, [3.5, 3.5], atol=.1)
        assert np.allclose(result.yhigh, [4.5, 5.83333333], atol=.1)

    def test_pi(self):

        stat = Est(errorbar="pi")
        groupby = GroupBy(["x"])

        data = pd.DataFrame(dict(x=[1, 1, 2, 2, 2], y=[3, 5, 2, 5, 7]))
        result = stat(data, groupby, "x", {})

        assert result.x.equals(pd.Series([1, 2], name="x"))
        assert np.allclose(result.y, [4, 4.66666667], atol=.1)
        assert np.allclose(result.ylow, [3, 2], atol=.1)
        assert np.allclose(result.yhigh, [5, 7], atol=.1)

    def test_pi_level(self):

        stat = Est(errorbar=("pi", 50))
        groupby = GroupBy(["x"])

        data = pd.DataFrame(dict(x=[1, 1, 2, 2, 2], y=[3, 5, 2, 5, 7]))
        result = stat(data, groupby, "x", {})

        assert result.x.equals(pd.Series([1, 2], name="x"))
        assert np.allclose(result.y, [4, 4.66666667], atol=.1)
        assert np.allclose(result.ylow, [3.5, 3.5], atol=.1)
        assert np.allclose(result.yhigh, [4.5, 5.83333333], atol=.1)

    def test_se(self):

        stat = Est(errorbar="se")
        groupby = GroupBy(["x"])

        data = pd.DataFrame(dict(x=[1, 1, 2, 2, 2], y=[3, 5, 2, 5, 7]))
        result = stat(data, groupby, "x", {})

        assert result.x.equals(pd.Series([1, 2], name="x"))
        assert np.allclose(result.y, [4, 4.66666667], atol=.1)
        assert np.allclose(result.ylow, [2.585, 3.446], atol=.1)
        assert np.allclose(result.yhigh, [5.415, 5.887], atol=.1)

    def test_se_level(self):

        stat = Est(errorbar=("se", 2))
        groupby = GroupBy(["x"])

        data = pd.DataFrame(dict(x=[1, 1, 2, 2, 2], y=[3, 5, 2, 5, 7]))
        result = stat(data, groupby, "x", {})

        assert result.x.equals(pd.Series([1, 2], name="x"))
        assert np.allclose(result.y, [4, 4.66666667], atol=.1)
        assert np.allclose(result.ylow, [1.17, 2.224], atol=.1)
        assert np.allclose(result.yhigh, [6.83, 7.109], atol=.1)

    def test_sd(self):

        stat = Est(errorbar="sd")
        groupby = GroupBy(["x"])

        data = pd.DataFrame(dict(x=[1, 1, 2, 2, 2], y=[3, 5, 2, 5, 7]))
        result = stat(data, groupby, "x", {})

        assert result.x.equals(pd.Series([1, 2], name="x"))
        assert np.allclose(result.y, [4, 4.66666667], atol=.1)
        assert np.allclose(result.ylow, [1.414, 2.054], atol=.1)
        assert np.allclose(result.yhigh, [6.586, 7.279], atol=.1)

    def test_sd_level(self):

        stat = Est(errorbar=("sd", 2))
        groupby = GroupBy(["x"])

        data = pd.DataFrame(dict(x=[1, 1, 2, 2, 2], y=[3, 5, 2, 5, 7]))
        result = stat(data, groupby, "x", {})

        assert result.x.equals(pd.Series([1, 2], name="x"))
        assert np.allclose(result.y, [4, 4.66666667], atol=.1)
        assert np.allclose(result.ylow, [-1.828, -0.558], atol=.1)
        assert np.allclose(result.yhigh, [9.828, 9.891], atol=.1)

    def test_custom_func(self):

        stat = Est(errorbar=np.ptp)
        groupby = GroupBy(["x"])

        data = pd.DataFrame(dict(x=[1, 1, 2, 2, 2], y=[3, 5, 2, 5, 7]))
        result = stat(data, groupby, "x", {})

        assert result.x.equals(pd.Series([1, 2], name="x"))
        assert np.allclose(result.y, [4, 4.66666667], atol=.1)
        assert np.allclose(result.ylow, [3, 2], atol=.1)
        assert np.allclose(result.yhigh, [5, 7], atol=.1)

    def test_error_method_none(self):

        stat = Est(errorbar=None)
        groupby = GroupBy(["x"])

        data = pd.DataFrame(dict(x=[1, 1, 2, 2, 2], y=[3, 5, 2, 5, 7]))
        result = stat(data, groupby, "x", {})

        assert result.x.equals(pd.Series([1, 2], name="x"))
        assert np.allclose(result.y, [4, 4.66666667], atol=.1)
        assert result.ylow.isna().all()
        assert result.yhigh.isna().all()

    def test_no_ci_with_single_observation(self):

        stat = Est(errorbar="ci")
        groupby = GroupBy(["x"])

        data = pd.DataFrame(dict(x=[1, 1, 2], y=[3, 5, 2]))
        result = stat(data, groupby, "x", {})

        assert result.x.equals(pd.Series([1, 2], name="x"))
        assert np.allclose(result.y, [4, 2], atol=.1)
        assert np.allclose(result.ylow, [2.897, np.nan], atol=.1)
        assert np.allclose(result.yhigh, [5.103, np.nan], atol=.1)

    def test_no_error_bars_with_single_observation(self):

        stat = Est(errorbar="sd")
        groupby = GroupBy(["x"])

        data = pd.DataFrame(dict(x=[1, 1, 2], y=[3, 5, 2]))
        result = stat(data, groupby, "x", {})

        assert result.x.equals(pd.Series([1, 2], name="x"))
        assert np.allclose(result.y, [4, 2], atol=.1)
        assert np.allclose(result.ylow, [1.414, np.nan], atol=.1)
        assert np.allclose(result.yhigh, [6.586, np.nan], atol=.1)

    def test_missing_values(self):

        stat = Est(errorbar="ci")
        groupby = GroupBy(["x"])

        data = pd.DataFrame(dict(x=[1, 1, 2, 2, 2], y=[3, 5, np.nan, 5, 7]))
        result = stat(data, groupby, "x", {})

        assert result.x.equals(pd.Series([1, 2], name="x"))
        assert np.allclose(result.y, [4, 6], atol=.1)
        assert np.allclose(result.ylow, [2.897, 4], atol=.1)
        assert np.allclose(result.yhigh, [5.103, 8], atol=.1)

    def test_missing_values_ci_custom_func(self):

        stat = Est(errorbar="ci")
        groupby = GroupBy(["x"])

        data = pd.DataFrame(dict(x=[1, 1, 2, 2, 2], y=[3, 5, np.nan, 5, 7]))
        result = stat(data, groupby, "x", {})

        assert result.x.equals(pd.Series([1, 2], name="x"))
        assert np.allclose(result.y, [4, 6], atol=.1)
        assert np.allclose(result.ylow, [2.897, 4], atol=.1)
        assert np.allclose(result.yhigh, [5.103, 8], atol=.1)

    def test_weighted(self):

        stat = Est(errorbar="ci")
        groupby = GroupBy(["x"])

        data = pd.DataFrame(dict(x=[1, 1, 2, 2, 2], y=[3, 5, 2, 5, 7], weight=[1, 2, 3, 1, 1]))
        result = stat(data, groupby, "x", {})

        assert result.x.equals(pd.Series([1, 2], name="x"))
        assert np.allclose(result.y, [4.333, 3.5], atol=.1)
        assert np.allclose(result.ylow, [2.567, 2.15], atol=.1)
        assert np.allclose(result.yhigh, [6.1, 4.85], atol=.1)

    def test_weighted_custom_func(self):

        stat = Est(errorbar="ci")
        groupby = GroupBy(["x"])

        data = pd.DataFrame(dict(x=[1, 1, 2, 2, 2], y=[3, 5, 2, 5, 7], weight=[1, 2, 3, 1, 1]))
        result = stat(data, groupby, "x", {})

        assert result.x.equals(pd.Series([1, 2], name="x"))
        assert np.allclose(result.y, [4.333, 3.5], atol=.1)
        assert np.allclose(result.ylow, [2.567, 2.15], atol=.1)
        assert np.allclose(result.yhigh, [6.1, 4.85], atol=.1)

    def test_weighted_error_method_none(self):

        stat = Est(errorbar=None)
        groupby = GroupBy(["x"])

        data = pd.DataFrame(dict(x=[1, 1, 2, 2, 2], y=[3, 5, 2, 5, 7], weight=[1, 2, 3, 1, 1]))
        result = stat(data, groupby, "x", {})

        assert result.x.equals(pd.Series([1, 2], name="x"))
        assert np.allclose(result.y, [4.333, 3.5], atol=.1)
        assert result.ylow.isna().all()
        assert result.yhigh.isna().all()

    @pytest.mark.parametrize(
        "param, kwargs",
        [
            ("func", dict(func="median")),
            ("errorbar", dict(errorbar="se")),
            ("n_boot", dict(n_boot=500)),
            ("seed", dict(seed=0)),
            ("errorbar", dict(errorbar=None)),
            ("errorbar", dict(errorbar="sd")),
        ],
    )
    def test_repr(self, param, kwargs):

        stat = Est(**kwargs)
        expected = f"Est({param}={repr(getattr(stat, param))})"
        assert repr(stat) == expected

    def test_repr_defaults(self):

        stat = Est()
        expected = (
            "Est(func='mean', errorbar=('ci', 95), n_boot=1000, seed=None)"
        )
        assert repr(stat) == expected

    def test_repr_non_defaults(self):

        stat = Est(
            func="median",
            errorbar="se",
            n_boot=500,
            seed=0,
        )
        expected = (
            "Est(func='median', errorbar=('se', 1), n_boot=500, seed=0)"
        )
        assert repr(stat) == expected

    def test_repr_seed_default(self):

        stat = Est(
            func="median",
            errorbar="se",
            n_boot=500,
        )
        expected = (
            "Est(func='median', errorbar=('se', 1), n_boot=500)"
        )
        assert repr(stat) == expected