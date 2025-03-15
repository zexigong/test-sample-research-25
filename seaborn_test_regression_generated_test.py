# Released under the BSD 3-clause license (see LICENSE)

import numpy as np
import pandas as pd
import pytest

from seaborn._core.groupby import GroupBy
from seaborn._stats.regression import PolyFit


class TestPolyFit:

    def test_fit_predict(self):

        df = pd.DataFrame(dict(x=[0, 1, 2, 3], y=[0, 1, 2, 3]))
        stat = PolyFit(order=1, gridsize=10)

        out = stat._fit_predict(df)
        assert out.shape == (10, 2)
        assert out["x"].min() == 0
        assert out["x"].max() == 3

        np.testing.assert_array_equal(out["x"], np.linspace(0, 3, 10))
        np.testing.assert_array_equal(out["y"], np.linspace(0, 3, 10))

    def test_fit_predict_empty(self):

        df = pd.DataFrame(dict(x=[1, 1], y=[0, 1]))
        stat = PolyFit(order=1, gridsize=10)

        out = stat._fit_predict(df)
        assert out.shape == (0, 2)

    def test_call(self):

        df = pd.DataFrame(dict(x=[0, 1, 2, 3], y=[0, 1, 2, 3], a=[0, 0, 1, 1]))
        stat = PolyFit(order=1, gridsize=10)
        groupby = GroupBy(["a"], sort=True)

        out = stat(df, groupby, None, None)

        assert out.shape == (20, 3)
        assert (out["a"] == 0).sum() == 10
        assert (out["a"] == 1).sum() == 10

        np.testing.assert_array_equal(out["x"], np.tile(np.linspace(0, 1, 10), 2))
        np.testing.assert_array_equal(out["y"], np.tile(np.linspace(0, 1, 10), 2))