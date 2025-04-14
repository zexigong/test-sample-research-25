"""Test the Agg stat."""
from __future__ import annotations
import numpy as np
import pandas as pd
import pytest

from seaborn._core.groupby import GroupBy
from seaborn._core.scales import Scale
from seaborn._stats.aggregation import Agg


class TestAgg:

    def test_default(self, long_df):

        p = Agg()
        g = GroupBy(["a", "c"])

        out = p(long_df, g, "x", {"x": Scale("linear")})

        x_means = long_df.groupby(["a", "c"])["y"].mean().values
        assert np.array_equal(out["y"], x_means)

    @pytest.mark.parametrize("func", ["min", "max", "median"])
    def test_string_func(self, long_df, func):

        p = Agg(func)
        g = GroupBy(["a", "c"])

        out = p(long_df, g, "x", {"x": Scale("linear")})

        x_agg = getattr(long_df.groupby(["a", "c"])["y"], func)().values
        assert np.array_equal(out["y"], x_agg)

    @pytest.mark.parametrize("func", [np.min, np.max, np.median])
    def test_numpy_func(self, long_df, func):

        p = Agg(func)
        g = GroupBy(["a", "c"])

        out = p(long_df, g, "x", {"x": Scale("linear")})

        x_agg = long_df.groupby(["a", "c"])["y"].agg(func).values
        assert np.array_equal(out["y"], x_agg)

    def test_custom_func(self, long_df):

        def foo(x):
            return x.iloc[0] - x.iloc[-1]

        p = Agg(foo)
        g = GroupBy(["a", "c"])

        out = p(long_df, g, "x", {"x": Scale("linear")})

        x_agg = long_df.groupby(["a", "c"])["y"].agg(foo).values
        assert np.array_equal(out["y"], x_agg)

    def test_orient(self, long_df):

        p = Agg()
        g = GroupBy(["a", "c"])

        out = p(long_df, g, "y", {"y": Scale("linear")})

        x_means = long_df.groupby(["a", "c"])["x"].mean().values
        assert np.array_equal(out["x"], x_means)

    def test_na(self, long_df):

        df = long_df.copy()
        df.loc[::2, "y"] = np.nan

        p = Agg()
        g = GroupBy(["a", "c"])

        out = p(df, g, "x", {"x": Scale("linear")})

        x_means = df.groupby(["a", "c"])["y"].mean().values
        assert np.array_equal(out["y"], x_means)

        assert out["y"].notna().all()

    def test_empty(self, long_df):

        df = long_df.iloc[[], :]

        p = Agg()
        g = GroupBy(["a", "c"])

        out = p(df, g, "x", {"x": Scale("linear")})

        assert out.empty