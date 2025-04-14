from __future__ import annotations
import itertools
import numpy as np
import pandas as pd
from pandas.testing import assert_frame_equal

import pytest

from seaborn._stats.counting import Count, Hist


class TestCount:

    def test_single_group(self):

        n = 100
        x = np.random.normal(size=n)
        data = pd.DataFrame(dict(x=x, y=1))

        stat = Count()
        out = stat(data, groupby=None, orient="x", scales=None)

        expected = pd.DataFrame(dict(x=x, y=1))
        assert_frame_equal(out, expected)

    def test_no_groups(self):

        n = 100
        x = np.random.normal(size=n)
        data = pd.DataFrame(dict(x=x))

        stat = Count()
        out = stat(data, groupby=None, orient="x", scales=None)

        expected = pd.DataFrame(dict(x=x, y=1))
        assert_frame_equal(out, expected)

    def test_multiple_groups(self):

        n = 100
        x = np.random.normal(size=n)
        g = ["a"] * (n // 2) + ["b"] * (n // 2)
        data = pd.DataFrame(dict(x=x, g=g))

        stat = Count()
        out = stat(data, groupby=None, orient="x", scales=None)

        expected = data.copy()
        expected["y"] = 1
        assert_frame_equal(out, expected)

    def test_orient_y(self):

        n = 100
        y = np.random.normal(size=n)
        data = pd.DataFrame(dict(y=y))

        stat = Count()
        out = stat(data, groupby=None, orient="y", scales=None)

        expected = pd.DataFrame(dict(y=y, x=1))
        assert_frame_equal(out, expected)


class TestHist:

    def test_single_group(self):

        n = 100
        x = np.random.normal(size=n)
        data = pd.DataFrame(dict(x=x))

        stat = Hist()
        out = stat(data, groupby=None, orient="x", scales=None)

        expected = pd.DataFrame(dict(
            x=[-2.75, -1.65, -0.55, 0.55, 1.65, 2.75],
            y=[5, 25, 31, 25, 10, 4],
            space=[1.1] * 6,
        ))
        assert_frame_equal(out, expected)

    def test_no_groups(self):

        n = 100
        x = np.random.normal(size=n)
        data = pd.DataFrame(dict(x=x))

        stat = Hist()
        out = stat(data, groupby=None, orient="x", scales=None)

        expected = pd.DataFrame(dict(
            x=[-2.75, -1.65, -0.55, 0.55, 1.65, 2.75],
            y=[5, 25, 31, 25, 10, 4],
            space=[1.1] * 6,
        ))
        assert_frame_equal(out, expected)

    def test_multiple_groups(self):

        n = 100
        x = np.random.normal(size=n)
        g = ["a"] * (n // 2) + ["b"] * (n // 2)
        data = pd.DataFrame(dict(x=x, g=g))

        stat = Hist()
        out = stat(data, groupby=None, orient="x", scales=None)

        expected = pd.DataFrame(dict(
            x=[-2.75, -1.65, -0.55, 0.55, 1.65, 2.75] * 2,
            y=[3, 12, 14, 12, 7, 2, 2, 13, 17, 13, 3, 2],
            space=[1.1] * 12,
            g=["a"] * 6 + ["b"] * 6,
        ))
        assert_frame_equal(out, expected)

    def test_orient_y(self):

        n = 100
        y = np.random.normal(size=n)
        data = pd.DataFrame(dict(y=y))

        stat = Hist()
        out = stat(data, groupby=None, orient="y", scales=None)

        expected = pd.DataFrame(dict(
            y=[-2.75, -1.65, -0.55, 0.55, 1.65, 2.75],
            x=[5, 25, 31, 25, 10, 4],
            space=[1.1] * 6,
        ))
        assert_frame_equal(out, expected)

    @pytest.mark.parametrize("orient", ["x", "y"])
    def test_discrete(self, orient):

        n = 100
        vals = np.random.randint(5, size=n)
        data = pd.DataFrame({orient: vals})

        stat = Hist(discrete=True)
        out = stat(data, groupby=None, orient=orient, scales=None)

        other = {"x": "y", "y": "x"}[orient]
        expected = pd.DataFrame({orient: np.arange(5), other: np.bincount(vals)})
        assert_frame_equal(out, expected)

    @pytest.mark.parametrize("cumulative", [True, False])
    @pytest.mark.parametrize("common_bins", [True, False])
    @pytest.mark.parametrize("common_norm", [True, False])
    def test_preset_binning(self, cumulative, common_bins, common_norm):

        # Regression test for https://github.com/mwaskom/seaborn/issues/3027

        # We're not going to reimplement binning here, just check that
        # using the same bin edges across groups gives the expected result
        # (which is to say, the same as it would when not using groups)

        rng = np.random.default_rng()
        n = 100
        g = np.repeat(["a", "b"], n)
        x = rng.normal(size=n * 2)
        data = pd.DataFrame(dict(g=g, x=x))

        hist = Hist(
            stat="count",
            cumulative=cumulative,
            common_bins=common_bins,
            common_norm=common_norm,
        )
        out = hist(data, groupby=None, orient="x", scales=None)

        hist = Hist(
            stat="count",
            cumulative=cumulative,
        )
        out_no_group = hist(data[["x"]], groupby=None, orient="x", scales=None)

        if common_bins:
            assert_frame_equal(
                out[["x", "space"]], out_no_group[["x", "space"]]
            )
            if common_norm:
                assert_frame_equal(
                    out["y"], out_no_group["y"].repeat(2).reset_index(drop=True)
                )