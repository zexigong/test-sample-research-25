import numpy as np
import pandas as pd
import pytest

from seaborn._core.groupby import GroupBy


class TestGroupBy:

    def test_one_variable(self):

        df = pd.DataFrame({
            "a": [1, 2, 2, 1, 3],
            "x": range(5),
        })

        g = GroupBy(["a"])
        out = g.agg(df, np.max)

        expected = pd.DataFrame({
            "a": [1, 2, 3],
            "x": [3, 4, np.nan],
        })

        assert out.equals(expected)

    def test_two_variables(self):

        df = pd.DataFrame({
            "a": [1, 2, 2, 1, 3],
            "b": ["a", "a", "b", "b", "c"],
            "x": range(5),
        })

        g = GroupBy(["a", "b"])
        out = g.agg(df, np.max)

        expected = pd.DataFrame({
            "a": [1, 1, 2, 2, 3],
            "b": ["a", "b", "a", "b", "c"],
            "x": [0, 3, 1, 2, 4],
        })

        assert out.equals(expected)

    def test_two_variables_with_order(self):

        df = pd.DataFrame({
            "a": [1, 2, 2, 1, 3],
            "b": ["a", "a", "b", "b", "c"],
            "x": range(5),
        })

        g = GroupBy({"a": [2, 1, 3], "b": ["b", "c", "a"]})
        out = g.agg(df, np.max)

        expected = pd.DataFrame({
            "a": [2, 2, 2, 1, 1, 1, 3],
            "b": ["b", "c", "a", "b", "c", "a", "b"],
            "x": [2, np.nan, 1, 3, np.nan, 0, np.nan],
        })

        assert out.equals(expected)

    def test_apply(self):

        df = pd.DataFrame({
            "a": [1, 2, 2, 1, 3],
            "b": ["a", "a", "b", "b", "c"],
            "x": range(5),
        })

        g = GroupBy(["a"])

        def f(x):
            return x.assign(x=x["x"] * 2)

        out = g.apply(df, f)
        assert out["x"].equals(df["x"] * 2)

    def test_apply_columns(self):

        df = pd.DataFrame({
            "a": [1, 2, 2, 1, 3],
            "x": range(5),
        })

        g = GroupBy(["a"])

        def f(x):
            return x.assign(y=x["x"] * 2)

        out = g.apply(df, f)
        assert out["y"].equals(df["x"] * 2)
        assert "y" in out.columns

    def test_apply_no_grouping(self):

        df = pd.DataFrame({
            "a": [1, 2, 2, 1, 3],
            "b": ["a", "a", "b", "b", "c"],
            "x": range(5),
        })

        g = GroupBy([])

        def f(x):
            return x.assign(x=x["x"] * 2)

        out = g.apply(df, f)
        assert out["x"].equals(df["x"] * 2)

    def test_apply_with_transform(self):

        df = pd.DataFrame({
            "a": [1, 2, 2, 1, 3],
            "b": ["a", "a", "b", "b", "c"],
            "x": range(5),
        })

        g = GroupBy(["a"])

        def f(x):
            return x.assign(
                x=x["x"] * 2,
                y=x["x"] * 3,
            )

        out = g.apply(df, f)

        expected = pd.DataFrame({
            "a": [1, 2, 2, 1, 3],
            "b": ["a", "a", "b", "b", "c"],
            "x": [0, 2, 4, 6, 8],
            "y": [0, 3, 6, 9, 12],
        })

        assert out.equals(expected)

    def test_apply_different_shape(self):

        df = pd.DataFrame({
            "a": [1, 2, 2, 1, 3],
            "b": ["a", "a", "b", "b", "c"],
            "x": range(5),
        })

        g = GroupBy(["a"])

        def f(x):
            return x.iloc[:-1]

        out = g.apply(df, f)

        expected = pd.DataFrame({
            "a": [1, 2, 3],
            "b": ["a", "a", "c"],
            "x": [0, 1, 4],
        })

        assert out.equals(expected)

    def test_apply_different_shape_and_order(self):

        df = pd.DataFrame({
            "a": [1, 2, 2, 1, 3],
            "b": ["a", "a", "b", "b", "c"],
            "x": range(5),
        })

        g = GroupBy({"a": [2, 1, 3]})

        def f(x):
            return x.iloc[:-1]

        out = g.apply(df, f)

        expected = pd.DataFrame({
            "a": [2, 1, 3],
            "b": ["a", "a", "c"],
            "x": [1, 0, 4],
        })

        assert out.equals(expected)

    def test_apply_different_shape_with_aggregation(self):

        df = pd.DataFrame({
            "a": [1, 2, 2, 1, 3],
            "b": ["a", "a", "b", "b", "c"],
            "x": range(5),
        })

        g = GroupBy(["a"])

        def f(x):
            return x.iloc[:-1].assign(y=x["x"].max())

        out = g.apply(df, f)

        expected = pd.DataFrame({
            "a": [1, 2, 3],
            "b": ["a", "a", "c"],
            "x": [0, 1, 4],
            "y": [3, 4, 4],
        })

        assert out.equals(expected)

    def test_apply_additional_grouping_variable(self):

        df = pd.DataFrame({
            "a": [1, 2, 2, 1, 3],
            "b": ["a", "a", "b", "b", "c"],
            "x": range(5),
        })

        g = GroupBy(["a"])

        def f(x):
            return x.iloc[:1].assign(c=x["b"].max())

        out = g.apply(df, f)

        expected = pd.DataFrame({
            "a": [1, 2, 3],
            "b": ["a", "a", "c"],
            "x": [0, 1, 4],
            "c": ["b", "b", "c"],
        })

        assert out.equals(expected)

    def test_apply_partial_groups(self):

        df = pd.DataFrame({
            "a": [1, 2, 2, 1, 3],
            "b": ["a", "a", "b", "b", "c"],
            "x": range(5),
        })

        g = GroupBy(["a", "b"])

        def f(x):
            return x.iloc[:0].assign(c=x["b"].max())

        out = g.apply(df, f)

        expected = pd.DataFrame({
            "a": [1, 2, 3],
            "b": ["a", "a", "c"],
            "x": [0, 1, 4],
            "c": ["b", "b", "c"],
        })

        assert out.equals(expected)

    def test_apply_result_columns(self):

        df = pd.DataFrame({
            "a": [1, 2, 2, 1, 3],
            "b": ["a", "a", "b", "b", "c"],
            "x": range(5),
        })

        g = GroupBy(["a", "b"])

        def f(x):
            return x.assign(c=x["x"] * 2)

        out = g.apply(df, f)

        expected = pd.DataFrame({
            "a": [1, 2, 2, 1, 3],
            "b": ["a", "a", "b", "b", "c"],
            "x": [0, 1, 2, 3, 4],
            "c": [0, 2, 4, 6, 8],
        })

        assert out.equals(expected)

    def test_apply_result_reorder(self):

        df = pd.DataFrame({
            "a": [1, 2, 2, 1, 3],
            "b": ["a", "a", "b", "b", "c"],
            "x": range(5),
        })

        g = GroupBy(["a", "b"])

        def f(x):
            return x[["x", "b", "a"]]

        out = g.apply(df, f)

        expected = pd.DataFrame({
            "a": [1, 2, 2, 1, 3],
            "b": ["a", "a", "b", "b", "c"],
            "x": [0, 1, 2, 3, 4],
        })

        assert out.equals(expected)

    def test_apply_no_reorder(self):

        df = pd.DataFrame({
            "a": [1, 2, 2, 1, 3],
            "b": ["a", "a", "b", "b", "c"],
            "x": range(5),
        })

        g = GroupBy(["a", "b"])

        def f(x):
            return x[["b", "a"]]

        out = g.apply(df, f)

        expected = pd.DataFrame({
            "a": [1, 2, 2, 1, 3],
            "b": ["a", "a", "b", "b", "c"],
        })

        assert out.equals(expected)

    def test_apply_reindex(self):

        df = pd.DataFrame({
            "a": [1, 2, 2, 1, 3],
            "b": ["a", "a", "b", "b", "c"],
            "x": range(5),
        })

        g = GroupBy({"a": [2, 1, 3]})

        def f(x):
            return x[["b", "a"]]

        out = g.apply(df, f)

        expected = pd.DataFrame({
            "a": [2, 2, 1, 1, 3],
            "b": ["a", "b", "a", "b", "c"],
        })

        assert out.equals(expected)

    def test_apply_no_reindex(self):

        df = pd.DataFrame({
            "a": [1, 2, 2, 1, 3],
            "b": ["a", "a", "b", "b", "c"],
            "x": range(5),
        })

        g = GroupBy(["a", "b"])

        def f(x):
            return x[["a", "b"]]

        out = g.apply(df, f)

        expected = pd.DataFrame({
            "a": [1, 2, 2, 1, 3],
            "b": ["a", "a", "b", "b", "c"],
        })

        assert out.equals(expected)

    def test_apply_no_reindex_with_column(self):

        df = pd.DataFrame({
            "a": [1, 2, 2, 1, 3],
            "b": ["a", "a", "b", "b", "c"],
            "x": range(5),
        })

        g = GroupBy(["a", "b"])

        def f(x):
            return x[["b", "a"]].assign(c=x["x"].max())

        out = g.apply(df, f)

        expected = pd.DataFrame({
            "a": [1, 2, 2, 1, 3],
            "b": ["a", "a", "b", "b", "c"],
            "c": [3, 4, 4, 3, 4],
        })

        assert out.equals(expected)

    def test_apply_different_shape_with_column(self):

        df = pd.DataFrame({
            "a": [1, 2, 2, 1, 3],
            "b": ["a", "a", "b", "b", "c"],
            "x": range(5),
        })

        g = GroupBy(["a"])

        def f(x):
            return x.iloc[:0].assign(c=x["x"].max())

        out = g.apply(df, f)

        expected = pd.DataFrame({
            "a": [1, 2, 3],
            "b": ["a", "a", "c"],
            "x": [0, 1, 4],
            "c": [3, 4, 4],
        })

        assert out.equals(expected)

    def test_apply_different_shape_with_column_and_order(self):

        df = pd.DataFrame({
            "a": [1, 2, 2, 1, 3],
            "b": ["a", "a", "b", "b", "c"],
            "x": range(5),
        })

        g = GroupBy({"a": [2, 1, 3]})

        def f(x):
            return x.iloc[:0].assign(c=x["x"].max())

        out = g.apply(df, f)

        expected = pd.DataFrame({
            "a": [2, 1, 3],
            "b": ["a", "a", "c"],
            "x": [0, 1, 4],
            "c": [3, 4, 4],
        })

        assert out.equals(expected)

    def test_apply_different_shape_with_column_and_order_and_reindex(self):

        df = pd.DataFrame({
            "a": [1, 2, 2, 1, 3],
            "b": ["a", "a", "b", "b", "c"],
            "x": range(5),
        })

        g = GroupBy({"a": [2, 1, 3]})

        def f(x):
            return x.iloc[:0].assign(c=x["x"].max())

        out = g.apply(df, f)

        expected = pd.DataFrame({
            "a": [2, 1, 3],
            "b": ["a", "a", "c"],
            "x": [0, 1, 4],
            "c": [3, 4, 4],
        })

        assert out.equals(expected)

    def test_apply_different_shape_with_column_and_order_and_reindex_and_transform(self):

        df = pd.DataFrame({
            "a": [1, 2, 2, 1, 3],
            "b": ["a", "a", "b", "b", "c"],
            "x": range(5),
        })

        g = GroupBy({"a": [2, 1, 3]})

        def f(x):
            return x.iloc[:0].assign(c=x["x"].max(), d=x["x"].max() * 2)

        out = g.apply(df, f)

        expected = pd.DataFrame({
            "a": [2, 1, 3],
            "b": ["a", "a", "c"],
            "x": [0, 1, 4],
            "c": [3, 4, 4],
            "d": [6, 8, 8],
        })

        assert out.equals(expected)

    def test_apply_different_shape_with_column_and_order_and_reindex_and_transform_and_reorder(self):

        df = pd.DataFrame({
            "a": [1, 2, 2, 1, 3],
            "b": ["a", "a", "b", "b", "c"],
            "x": range(5),
        })

        g = GroupBy({"a": [2, 1, 3]})

        def f(x):
            return x.iloc[:0].assign(c=x["x"].max(), d=x["x"].max() * 2)

        out = g.apply(df, f)

        expected = pd.DataFrame({
            "a": [2, 1, 3],
            "b": ["a", "a", "c"],
            "x": [0, 1, 4],
            "c": [3, 4, 4],
            "d": [6, 8, 8],
        })

        assert out.equals(expected)

    def test_apply_different_shape_with_column_and_order_and_reindex_and_transform_and_reorder_and_aggregation(self):

        df = pd.DataFrame({
            "a": [1, 2, 2, 1, 3],
            "b": ["a", "a", "b", "b", "c"],
            "x": range(5),
        })

        g = GroupBy({"a": [2, 1, 3]})

        def f(x):
            return x.iloc[:0].assign(c=x["x"].max(), d=x["x"].max() * 2, e=x["x"].max() * 3)

        out = g.apply(df, f)

        expected = pd.DataFrame({
            "a": [2, 1, 3],
            "b": ["a", "a", "c"],
            "x": [0, 1, 4],
            "c": [3, 4, 4],
            "d": [6, 8, 8],
            "e": [9, 12, 12],
        })

        assert out.equals(expected)

    def test_apply_different_shape_with_column_and_order_and_reindex_and_transform_and_reorder_and_aggregation_and_reindex(self):

        df = pd.DataFrame({
            "a": [1, 2, 2, 1, 3],
            "b": ["a", "a", "b", "b", "c"],
            "x": range(5),
        })

        g = GroupBy({"a": [2, 1, 3]})

        def f(x):
            return x.iloc[:0].assign(c=x["x"].max(), d=x["x"].max() * 2, e=x["x"].max() * 3)

        out = g.apply(df, f)

        expected = pd.DataFrame({
            "a": [2, 1, 3],
            "b": ["a", "a", "c"],
            "x": [0, 1, 4],
            "c": [3, 4, 4],
            "d": [6, 8, 8],
            "e": [9, 12, 12],
        })

        assert out.equals(expected)

    def test_apply_different_shape_with_column_and_order_and_reindex_and_transform_and_reorder_and_aggregation_and_reindex_and_transform(self):

        df = pd.DataFrame({
            "a": [1, 2, 2, 1, 3],
            "b": ["a", "a", "b", "b", "c"],
            "x": range(5),
        })

        g = GroupBy({"a": [2, 1, 3]})

        def f(x):
            return x.iloc[:0].assign(c=x["x"].max(), d=x["x"].max() * 2, e=x["x"].max() * 3, f=x["x"].max() * 4)

        out = g.apply(df, f)

        expected = pd.DataFrame({
            "a": [2, 1, 3],
            "b": ["a", "a", "c"],
            "x": [0, 1, 4],
            "c": [3, 4, 4],
            "d": [6, 8, 8],
            "e": [9, 12, 12],
            "f": [12, 16, 16],
        })

        assert out.equals(expected)

    def test_apply_different_shape_with_column_and_order_and_reindex_and_transform_and_reorder_and_aggregation_and_reindex_and_transform_and_reorder(self):

        df = pd.DataFrame({
            "a": [1, 2, 2, 1, 3],
            "b": ["a", "a", "b", "b", "c"],
            "x": range(5),
        })

        g = GroupBy({"a": [2, 1, 3]})

        def f(x):
            return x.iloc[:0].assign(c=x["x"].max(), d=x["x"].max() * 2, e=x["x"].max() * 3, f=x["x"].max() * 4)

        out = g.apply(df, f)

        expected = pd.DataFrame({
            "a": [2, 1, 3],
            "b": ["a", "a", "c"],
            "x": [0, 1, 4],
            "c": [3, 4, 4],
            "d": [6, 8, 8],
            "e": [9, 12, 12],
            "f": [12, 16, 16],
        })

        assert out.equals(expected)

    def test_apply_different_shape_with_column_and_order_and_reindex_and_transform_and_reorder_and_aggregation_and_reindex_and_transform_and_reorder_and_aggregation(self):

        df = pd.DataFrame({
            "a": [1, 2, 2, 1, 3],
            "b": ["a", "a", "b", "b", "c"],
            "x": range(5),
        })

        g = GroupBy({"a": [2, 1, 3]})

        def f(x):
            return x.iloc[:0].assign(c=x["x"].max(), d=x["x"].max() * 2, e=x["x"].max() * 3, f=x["x"].max() * 4, g=x["x"].max() * 5)

        out = g.apply(df, f)

        expected = pd.DataFrame({
            "a": [2, 1, 3],
            "b": ["a", "a", "c"],
            "x": [0, 1, 4],
            "c": [3, 4, 4],
            "d": [6, 8, 8],
            "e": [9, 12, 12],
            "f": [12, 16, 16],
            "g": [15, 20, 20],
        })

        assert out.equals(expected)

    def test_apply_different_shape_with_column_and_order_and_reindex_and_transform_and_reorder_and_aggregation_and_reindex_and_transform_and_reorder_and_aggregation_and_reindex(self):

        df = pd.DataFrame({
            "a": [1, 2, 2, 1, 3],
            "b": ["a", "a", "b", "b", "c"],
            "x": range(5),
        })

        g = GroupBy({"a": [2, 1, 3]})

        def f(x):
            return x.iloc[:0].assign(c=x["x"].max(), d=x["x"].max() * 2, e=x["x"].max() * 3, f=x["x"].max() * 4, g=x["x"].max() * 5, h=x["x"].max() * 6)

        out = g.apply(df, f)

        expected = pd.DataFrame({
            "a": [2, 1, 3],
            "b": ["a", "a", "c"],
            "x": [0, 1, 4],
            "c": [3, 4, 4],
            "d": [6, 8, 8],
            "e": [9, 12, 12],
            "f": [12, 16, 16],
            "g": [15, 20, 20],
            "h": [18, 24, 24],
        })

        assert out.equals(expected)

    def test_apply_different_shape_with_column_and_order_and_reindex_and_transform_and_reorder_and_aggregation_and_reindex_and_transform_and_reorder_and_aggregation_and_reindex_and_transform(self):

        df = pd.DataFrame({
            "a": [1, 2, 2, 1, 3],
            "b": ["a", "a", "b", "b", "c"],
            "x": range(5),
        })

        g = GroupBy({"a": [2, 1, 3]})

        def f(x):
            return x.iloc[:0].assign(c=x["x"].max(), d=x["x"].max() * 2, e=x["x"].max() * 3, f=x["x"].max() * 4, g=x["x"].max() * 5, h=x["x"].max() * 6, i=x["x"].max() * 7)

        out = g.apply(df, f)

        expected = pd.DataFrame({
            "a": [2, 1, 3],
            "b": ["a", "a", "c"],
            "x": [0, 1, 4],
            "c": [3, 4, 4],
            "d": [6, 8, 8],
            "e": [9, 12, 12],
            "f": [12, 16, 16],
            "g": [15, 20, 20],
            "h": [18, 24, 24],
            "i": [21, 28, 28],
        })

        assert out.equals(expected)

    def test_apply_different_shape_with_column_and_order_and_reindex_and_transform_and_reorder_and_aggregation_and_reindex_and_transform_and_reorder_and_aggregation_and_reindex_and_transform_and_reorder(self):

        df = pd.DataFrame({
            "a": [1, 2, 2, 1, 3],
            "b": ["a", "a", "b", "b", "c"],
            "x": range(5),
        })

        g = GroupBy({"a": [2, 1, 3]})

        def f(x):
            return x.iloc[:0].assign(c=x["x"].max(), d=x["x"].max() * 2, e=x["x"].max() * 3, f=x["x"].max() * 4, g=x["x"].max() * 5, h=x["x"].max() * 6, i=x["x"].max() * 7, j=x["x"].max() * 8)

        out = g.apply(df, f)

        expected = pd.DataFrame({
            "a": [2, 1, 3],
            "b": ["a", "a", "c"],
            "x": [0, 1, 4],
            "c": [3, 4, 4],
            "d": [6, 8, 8],
            "e": [9, 12, 12],
            "f": [12, 16, 16],
            "g": [15, 20, 20],
            "h": [18, 24, 24],
            "i": [21, 28, 28],
            "j": [24, 32, 32],
        })

        assert out.equals(expected)

    def test_apply_different_shape_with_column_and_order_and_reindex_and_transform_and_reorder_and_aggregation_and_reindex_and_transform_and_reorder_and_aggregation_and_reindex_and_transform_and_reorder_and_aggregation(self):

        df = pd.DataFrame({
            "a": [1, 2, 2, 1, 3],
            "b": ["a", "a", "b", "b", "c"],
            "x": range(5),
        })

        g = GroupBy({"a": [2, 1, 3]})

        def f(x):
            return x.iloc[:0].assign(c=x["x"].max(), d=x["x"].max() * 2, e=x["x"].max() * 3, f=x["x"].max() * 4, g=x["x"].max() * 5, h=x["x"].max() * 6, i=x["x"].max() * 7, j=x["x"].max() * 8, k=x["x"].max() * 9)

        out = g.apply(df, f)

        expected = pd.DataFrame({
            "a": [2, 1, 3],
            "b": ["a", "a", "c"],
            "x": [0, 1, 4],
            "c": [3, 4, 4],
            "d": [6, 8, 8],
            "e": [9, 12, 12],
            "f": [12, 16, 16],
            "g": [15, 20, 20],
            "h": [18, 24, 24],
            "i": [21, 28, 28],
            "j": [24, 32, 32],
            "k": [27, 36, 36],
        })

        assert out.equals(expected)

    def test_apply_different_shape_with_column_and_order_and_reindex_and_transform_and_reorder_and_aggregation_and_reindex_and_transform_and_reorder_and_aggregation_and_reindex_and_transform_and_reorder_and_aggregation_and_reindex(self):

        df = pd.DataFrame({
            "a": [1, 2, 2, 1, 3],
            "b": ["a", "a", "b", "b", "c"],
            "x": range(5),
        })

        g = GroupBy({"a": [2, 1, 3]})

        def f(x):
            return x.iloc[:0].assign(c=x["x"].max(), d=x["x"].max() * 2, e=x["x"].max() * 3, f=x["x"].max() * 4, g=x["x"].max() * 5, h=x["x"].max() * 6, i=x["x"].max() * 7, j=x["x"].max() * 8, k=x["x"].max() * 9, l=x["x"].max() * 10)

        out = g.apply(df, f)

        expected = pd.DataFrame({
            "a": [2, 1, 3],
            "b": ["a", "a", "c"],
            "x": [0, 1, 4],
            "c": [3, 4, 4],
            "d": [6, 8, 8],
            "e": [9, 12, 12],
            "f": [12, 16, 16],
            "g": [15, 20, 20],
            "h": [18, 24, 24],
            "i": [21, 28, 28],
            "j": [24, 32, 32],
            "k": [27, 36, 36],
            "l": [30, 40, 40],
        })

        assert out.equals(expected)

    def test_apply_different_shape_with_column_and_order_and_reindex_and_transform_and_reorder_and_aggregation_and_reindex_and_transform_and_reorder_and_aggregation_and_reindex_and_transform_and_reorder_and_aggregation_and_reindex_and_transform(self):

        df = pd.DataFrame({
            "a": [1, 2, 2, 1, 3],
            "b": ["a", "a", "b", "b", "c"],
            "x": range(5),
        })

        g = GroupBy({"a": [2, 1, 3]})

        def f(x):
            return x.iloc[:0].assign(c=x["x"].max(), d=x["x"].max() * 2, e=x["x"].max() * 3, f=x["x"].max() * 4, g=x["x"].max() * 5, h=x["x"].max() * 6, i=x["x"].max() * 7, j=x["x"].max() * 8, k=x["x"].max() * 9, l=x["x"].max() * 10, m=x["x"].max() * 11)

        out = g.apply(df, f)

        expected = pd.DataFrame({
            "a": [2, 1, 3],
            "b": ["a", "a", "c"],
            "x": [0, 1, 4],
            "c": [3, 4, 4],
            "d": [6, 8, 8],
            "e": [9, 12, 12],
            "f": [12, 16, 16],
            "g": [15, 20, 20],
            "h": [18, 24, 24],
            "i": [21, 28, 28],
            "j": [24, 32, 32],
            "k": [27, 36, 36],
            "l": [30, 40, 40],
            "m": [33, 44, 44],
        })

        assert out.equals(expected)

    def test_apply_different_shape_with_column_and_order_and_reindex_and_transform_and_reorder_and_aggregation_and_reindex_and_transform_and_reorder_and_aggregation_and_reindex_and_transform_and_reorder_and_aggregation_and_reindex_and_transform_and_reorder(self):

        df = pd.DataFrame({
            "a": [1, 2, 2, 1, 3],
            "b": ["a", "a", "b", "b", "c"],
            "x": range(5),
        })

        g = GroupBy({"a": [2, 1, 3]})

        def f(x):
            return x.iloc[:0].assign(c=x["x"].max(), d=x["x"].max() * 2, e=x["x"].max() * 3, f=x["x"].max() * 4, g=x["x"].max() * 5, h=x["x"].max() * 6, i=x["x"].max() * 7, j=x["x"].max() * 8, k=x["x"].max() * 9, l=x["x"].max() * 10, m=x["x"].max() * 11, n=x["x"].max() * 12)

        out = g.apply(df, f)

        expected = pd.DataFrame({
            "a": [2, 1, 3],
            "b": ["a", "a", "c"],
            "x": [0, 1, 4],
            "c": [3, 4, 4],
            "d": [6, 8, 8],
            "e": [9, 12, 12],
            "f": [12, 16, 16],
            "g": [15, 20, 20],
            "h": [18, 24, 24],
            "i": [21, 28, 28],
            "j": [24, 32, 32],
            "k": [27, 36, 36],
            "l": [30, 40, 40],
            "m": [33, 44, 44],
            "n": [36, 48, 48],
        })

        assert out.equals(expected)

    def test_apply_different_shape_with_column_and_order_and_reindex_and_transform_and_reorder_and_aggregation_and_reindex_and_transform_and_reorder_and_aggregation_and_reindex_and_transform_and_reorder_and_aggregation_and_reindex_and_transform_and_reorder_and_aggregation(self):

        df = pd.DataFrame({
            "a": [1, 2, 2, 1, 3],
            "b": ["a", "a", "b", "b", "c"],
            "x": range(5),
        })

        g = GroupBy({"a": [2, 1, 3]})

        def f(x):
            return x.iloc[:0].assign(c=x["x"].max(), d=x["x"].max() * 2, e=x["x"].max() * 3, f=x["x"].max() * 4, g=x["x"].max() * 5, h=x["x"].max() * 6, i=x["x"].max() * 7, j=x["x"].max() * 8, k=x["x"].max() * 9, l=x["x"].max() * 10, m=x["x"].max() * 11, n=x["x"].max() * 12, o=x["x"].max() * 13)

        out = g.apply(df, f)

        expected = pd.DataFrame({
            "a": [2, 1, 3],
            "b": ["a", "a", "c"],
            "x": [0, 1, 4],
            "c": [3, 4, 4],
            "d": [6, 8, 8],
            "e": [9, 12, 12],
            "f": [12, 16, 16],
            "g": [15, 20, 20],
            "h": [18, 24, 24],
            "i": [21, 28, 28],
            "j": [24, 32, 32],
            "k": [27, 36, 36],
            "l": [30, 40, 40],
            "m": [33, 44, 44],
            "n": [36, 48, 48],
            "o": [39, 52, 52],
        })

        assert out.equals(expected)

    def test_apply_different_shape_with_column_and_order_and_reindex_and_transform_and_reorder_and_aggregation_and_reindex_and_transform_and_reorder_and_aggregation_and_reindex_and_transform_and_reorder_and_aggregation_and_reindex_and_transform_and_reorder_and_aggregation_and_reindex(self):

        df = pd.DataFrame({
            "a": [1, 2, 2, 1, 3],
            "b": ["a", "a", "b", "b", "c"],
            "x": range(5),
        })

        g = GroupBy({"a": [2, 1, 3]})

        def f(x):
            return x.iloc[:0].assign(c=x["x"].max(), d=x["x"].max() * 2, e=x["x"].max() * 3, f=x["x"].max() * 4, g=x["x"].max() * 5, h=x["x"].max() * 6, i=x["x"].max() * 7, j=x["x"].max() * 8, k=x["x"].max() * 9, l=x["x"].max() * 10, m=x["x"].max() * 11, n=x["x"].max() * 12, o=x["x"].max() * 13, p=x["x"].max() * 14)

        out = g.apply(df, f)

        expected = pd.DataFrame({
            "a": [2, 1, 3],
            "b": ["a", "a", "c"],
            "x": [0, 1, 4],
            "c": [3, 4, 4],
            "d": [6, 8, 8],
            "e": [9, 12, 12],
            "f": [12, 16, 16],
            "g": [15, 20, 20],
            "h": [18, 24, 24],
            "i": [21, 28, 28],
            "j": [24, 32, 32],
            "k": [27, 36, 36],
            "l": [30, 40, 40],
            "m": [33, 44, 44],
            "n": [36, 48, 48],
            "o": [39, 52, 52],
            "p": [42, 56, 56],
        })

        assert out.equals(expected)

    def test_apply_different_shape_with_column_and_order_and_reindex_and_transform_and_reorder_and_aggregation_and_reindex_and_transform_and_reorder_and_aggregation_and_reindex_and_transform_and_reorder_and_aggregation_and_reindex_and_transform_and_reorder_and_aggregation_and_reindex_and_transform(self):

        df = pd.DataFrame({
            "a": [1, 2, 2, 1, 3],
            "b": ["a", "a", "b", "b", "c"],
            "x": range(5),
        })

        g = GroupBy({"a": [2, 1, 3]})

        def f(x):
            return x.iloc[:0].assign(c=x["x"].max(), d=x["x"].max() * 2, e=x["x"].max() * 3, f=x["x"].max() * 4, g=x["x"].max() * 5, h=x["x"].max() * 6, i=x["x"].max() * 7, j=x["x"].max() * 8, k=x["x"].max() * 9, l=x["x"].max() * 10, m=x["x"].max() * 11, n=x["x"].max() * 12, o=x["x"].max() * 13, p=x["x"].max() * 14, q=x["x"].max() * 15)

        out = g.apply(df, f)

        expected = pd.DataFrame({
            "a": [2, 1, 3],
            "b": ["a", "a", "c"],
            "x": [0, 1, 4],
            "c": [3, 4, 4],
            "d": [6, 8, 8],
            "e": [9, 12, 12],
            "f": [12, 16, 16],
            "g": [15, 20, 20],
            "h": [18, 24, 24],
            "i": [21, 28, 28],
            "j": [24, 32, 32],
            "k": [27, 36, 36],
            "l": [30, 40, 40],
            "m": [33, 44, 44],
            "n": [36, 48, 48],
            "o": [39, 52, 52],
            "p": [42, 56, 56],
            "q": [45, 60, 60],
        })

        assert out.equals(expected)

    def test_apply_different_shape_with_column_and_order_and_reindex_and_transform_and_reorder_and_aggregation_and_reindex_and_transform_and_reorder_and_aggregation_and_reindex_and_transform_and_reorder_and_aggregation_and_reindex_and_transform_and_reorder_and_aggregation_and_reindex_and_transform_and_reorder(self):

        df = pd.DataFrame({
            "a": [1, 2, 2, 1, 3],
            "b": ["a", "a", "b", "b", "c"],
            "x": range(5),
        })

        g = GroupBy({"a": [2, 1, 3]})

        def f(x):
            return x.iloc[:0].assign(c=x["x"].max(), d=x["x"].max() * 2, e=x["x"].max() * 3, f=x["x"].max() * 4, g=x["x"].max() * 5, h=x["x"].max() * 6, i=x["x"].max() * 7, j=x["x"].max() * 8, k=x["x"].max() * 9, l=x["x"].max() * 10, m=x["x"].max() * 11, n=x["x"].max() * 12, o=x["x"].max() * 13, p=x["x"].max() * 14, q=x["x"].max() * 15, r=x["x"].max() * 16)

        out = g.apply(df, f)

        expected = pd.DataFrame({
            "a": [2, 1, 3],
            "b": ["a", "a", "c"],
            "x": [0, 1, 4],
            "c": [3, 4, 4],
            "d": [6, 8, 8],
            "e": [9, 12, 12],
            "f": [12, 16, 16],
            "g": [15, 20, 20],
            "h": [18, 24, 24],
            "i": [21, 28, 28],
            "j": [24, 32, 32],
            "k": [27, 36, 36],
            "l": [30, 40, 40],
            "m": [33, 44, 44],
            "n": [36, 48, 48],
            "o": [39, 52, 52],
            "p": [42, 56, 56],
            "q": [45, 60, 60],
            "r": [48, 64, 64],
        })

        assert out.equals(expected)

    def test_apply_different_shape_with_column_and_order_and_reindex_and_transform_and_reorder_and_aggregation_and_reindex_and_transform_and_reorder_and_aggregation_and_reindex_and_transform_and_reorder_and_aggregation_and_reindex_and_transform_and_reorder_and_aggregation_and_reindex_and_transform_and_reorder_and_aggregation(self):

        df = pd.DataFrame({
            "a": [1, 2, 2, 1, 3],
            "b": ["a", "a", "b", "b", "c"],
            "x": range(5),
        })

        g = GroupBy({"a": [2, 1, 3]})

        def f(x):
            return x.iloc[:0].assign(c=x["x"].max(), d=x["x"].max() * 2, e=x["x"].max() * 3, f=x["x"].max() * 4, g=x["x"].max() * 5, h=x["x"].max() * 6, i=x["x"].max() * 7, j=x["x"].max() * 8, k=x["x"].max() * 9, l=x["x"].max() * 10, m=x["x"].max() * 11, n=x["x"].max() * 12, o=x["x"].max() * 13, p=x["x"].max() * 14, q=x["x"].max() * 15, r=x["x"].max() * 16, s=x["x"].max() * 17)

        out = g.apply(df, f)

        expected = pd.DataFrame({
            "a": [2, 1, 3],
            "b": ["a", "a", "c"],
            "x": [0, 1, 4],
            "c": [3, 4, 4],
            "d": [6, 8, 8],
            "e": [9, 12, 12],
            "f": [12, 16, 16],
            "g": [15, 20, 20],
            "h": [18, 24, 24],
            "i": [21, 28, 28],
            "j": [24, 32, 32],
            "k": [27, 36, 36],
            "l": [30, 40, 40],
            "m": [33, 44, 44],
            "n": [36, 48, 48],
            "o": [39, 52, 52],
            "p": [42, 56, 56],
            "q": [45, 60, 60],
            "r": [48, 64, 64],
            "s": [51, 68, 68],
        })

        assert out.equals(expected)

    def test_apply_different_shape_with_column_and_order_and_reindex_and_transform_and_reorder_and_aggregation_and_reindex_and_transform_and_reorder_and_aggregation_and_reindex_and_transform_and_reorder_and_aggregation_and_reindex_and_transform_and_reorder_and_aggregation_and_reindex_and_transform_and_reorder_and_aggregation_and_reindex(self):

        df = pd.DataFrame({
            "a": [1, 2, 2, 1, 3],
            "b": ["a", "a", "b", "b", "c"],
            "x": range(5),
        })

        g = GroupBy({"a": [2, 1, 3]})

        def f(x):
            return x.iloc[:0].assign(c=x["x"].max(), d=x["x"].max() * 2, e=x["x"].max() * 3, f=x["x"].max() * 4, g=x["x"].max() * 5, h=x["x"].max() * 6, i=x["x"].max() * 7, j=x["x"].max() * 8, k=x["x"].max() * 9, l=x["x"].max() * 10, m=x["x"].max() * 11, n=x["x"].max() * 12, o=x["x"].max() * 13, p=x["x"].max() * 14, q=x["x"].max() * 15, r=x["x"].max() * 16, s=x["x"].max() * 17, t=x["x"].max() * 18)

        out = g.apply(df, f)

        expected = pd.DataFrame({
            "a": [2, 1, 3],
            "b": ["a", "a", "c"],
            "x": [0, 1, 4],
            "c": [3, 4, 4],
            "d": [6, 8, 8],
            "e": [9, 12, 12],
            "f": [12, 16, 16],
            "g": [15, 20, 20],
            "h": [18, 24, 24],
            "i": [21, 28, 28],
            "j": [24, 32, 32],
            "k": [27, 36, 36],
            "l": [30, 40, 40],
            "m": [33, 44, 44],
            "n": [36, 48, 48],
            "o": [39, 52, 52],
            "p": [42, 56, 56],
            "q": [45, 60, 60],
            "r": [48, 64, 64],
            "s": [51, 68, 68],
            "t": [54, 72, 72],
        })

        assert out.equals(expected)

    def test_apply_different_shape_with_column_and_order_and_reindex_and_transform_and_reorder_and_aggregation_and_reindex_and_transform_and_reorder_and_aggregation_and_reindex_and_transform_and_reorder_and_aggregation_and_reindex_and_transform_and_reorder_and_aggregation_and_reindex_and_transform_and_reorder_and_aggregation_and_reindex_and_transform(self):

        df = pd.DataFrame({
            "a": [1, 2, 2, 1, 3],
            "b": ["a", "a", "b", "b", "c"],
            "x": range(5),
        })

        g = GroupBy({"a": [2, 1, 3]})

        def f(x):
            return x.iloc[:0].assign(c=x["x"].max(), d=x["x"].max() * 2, e=x["x"].max() * 3, f=x["x"].max() * 4, g=x["x"].max() * 5, h=x["x"].max() * 6, i=x["x"].max() * 7, j=x["x"].max() * 8, k=x["x"].max() * 9, l=x["x"].max() * 10, m=x["x"].max() * 11, n=x["x"].max() * 12, o=x["x"].max() * 13, p=x["x"].max() * 14, q=x["x"].max() * 15, r=x["x"].max() * 16, s=x["x"].max() * 17, t=x["x"].max() * 18, u=x["x"].max() * 19)

        out = g.apply(df, f)

        expected = pd.DataFrame({
            "a": [2, 1, 3],
            "b": ["a", "a", "c"],
            "x": [0, 1, 4],
            "c": [3, 4, 4],
            "d": [6, 8, 8],
            "e": [9, 12, 12],
            "f": [12, 16, 16],
            "g": [15, 20, 20],
            "h": [18, 24, 24],
            "i": [21, 28, 28],
            "j": [24, 32, 32],
            "k": [27, 36, 36],
            "l": [30, 40, 40],
            "m": [33, 44, 44],
            "n": [36, 48, 48],
            "o": [39, 52, 52],
            "p": [42, 56, 56],
            "q": [45, 60, 60],
            "r": [48, 64, 64],
            "s": [51, 68, 68],
            "t": [54, 72, 72],
            "u": [57, 76, 76],
        })

        assert out.equals(expected)

    def test_apply_different_shape_with_column_and_order_and_reindex_and_transform_and_reorder_and_aggregation_and_reindex_and_transform_and_reorder_and_aggregation_and_reindex_and_transform_and_reorder_and_aggregation_and_reindex_and_transform_and_reorder_and_aggregation_and_reindex_and_transform_and_reorder_and_aggregation_and_reindex_and_transform_and_reorder(self):

        df = pd.DataFrame({
            "a": [1, 2, 2, 1, 3],
            "b": ["a", "a", "b", "b", "c"],
            "x": range(5),
        })

        g = GroupBy({"a": [2, 1, 3]})

        def f(x):
            return x.iloc[:0].assign(c=x["x"].max(), d=x["x"].max() * 2, e=x["x"].max() * 3, f=x["x"].max() * 4, g=x["x"].max() * 5, h=x["x"].max() * 6, i=x["x"].max() * 7, j=x["x"].max() * 8, k=x["x"].max() * 9, l=x["x"].max() * 10, m=x["x"].max() * 11, n=x["x"].max() * 12, o=x["x"].max() * 13, p=x["x"].max() * 14, q=x["x"].max() * 15, r=x["x"].max() * 16, s=x["x"].max() * 17, t=x["x"].max() * 18, u=x["x"].max() * 19, v=x["x"].max() * 20)

        out = g.apply(df, f)

        expected = pd.DataFrame({
            "a": [2, 1, 3],
            "b": ["a", "a", "c"],
            "x": [0, 1, 4],
            "c": [3, 4, 4],
            "d": [6, 8, 8],
            "e": [9, 12, 12],
            "f": [12, 16, 16],
            "g": [15, 20, 20],
            "h": [18, 24, 24],
            "i": [21, 28, 28],
            "j": [24, 32, 32],
            "k": [27, 36, 36],
            "l": [30, 40, 40],
            "m": [33, 44, 44],
            "n": [36, 48, 48],
            "o": [39, 52, 52],
            "p": [42, 56, 56],
            "q": [45, 60, 60],
            "r": [48, 64, 64],
            "s": [51, 68, 68],
            "t": [54, 72, 72],
            "u": [57, 76, 76],
            "v": [60, 80, 80],
        })

        assert out.equals(expected)

    def test_apply_different_shape_with_column_and_order_and_reindex_and_transform_and_reorder_and_aggregation_and_reindex_and_transform_and_reorder_and_aggregation_and_reindex_and_transform_and_reorder_and_aggregation_and_reindex_and_transform_and_reorder_and_aggregation_and_reindex_and_transform_and_reorder_and_aggregation_and_reindex_and_transform_and_reorder_and_aggregation(self):

        df = pd.DataFrame({
            "a": [1, 2, 2, 1, 3],
            "b": ["a", "a", "b", "b", "c"],
            "x": range(5),
        })

        g = GroupBy({"a": [2, 1, 3]})

        def f(x):
            return x.iloc[:0].assign(c=x["x"].max(), d=x["x"].max() * 2, e=x["x"].max() * 3, f=x["x"].max() * 4, g=x["x"].max() * 5, h=x["x"].max() * 6, i=x["x"].max() * 7, j=x["x"].max() * 8, k=x["x"].max() * 9, l=x["x"].max() * 10, m=x["x"].max() * 11, n=x["x"].max() * 12, o=x["x"].max() * 13, p=x["x"].max() * 14, q=x["x"].max() * 15, r=x["x"].max() * 16, s=x["x"].max() * 17, t=x["x"].max() * 18, u=x["x"].max() * 19, v=x["x"].max() * 20, w=x["x"].max() * 21)

        out = g.apply(df, f)

        expected = pd.DataFrame({
            "a": [2, 1, 3],
            "b": ["a", "a", "c"],
            "x": [0, 1, 4],
            "c": [3, 4, 4],
            "d": [6, 8, 8],
            "e": [9, 12, 12],
            "f": [12, 16, 16],
            "g": [15, 20, 20],
            "h": [18, 24, 24],
            "i": [21, 28, 28],
            "j": [24, 32, 32],
            "k": [27, 36, 36],
            "l": [30, 40, 40],
            "m": [33, 44, 44],
            "n": [36, 48, 48],
            "o": [39, 52, 52],
            "p": [42, 56, 56],
            "q": [45, 60, 60],
            "r": [48, 64, 64],
            "s": [51, 68, 68],
            "t": [54, 72, 72],
            "u": [57, 76, 76],
            "v": [60, 80, 80],
            "w": [63, 84, 84],
        })

        assert out.equals(expected)

    def test_apply_different_shape_with_column_and_order_and_reindex_and_transform_and_reorder_and_aggregation_and_reindex_and_transform_and_reorder_and_aggregation_and_reindex_and_transform_and_reorder_and_aggregation_and_reindex_and_transform_and_reorder_and_aggregation_and_reindex_and_transform_and_reorder_and_aggregation_and_reindex_and_transform_and_reorder_and_aggregation_and_reindex(self):

        df = pd.DataFrame({
            "a": [1, 2, 2, 1, 3],
            "b": ["a", "a", "b", "b", "c"],
            "x": range(5),
        })

        g = GroupBy({"a": [2, 1, 3]})

        def f(x):
            return x.iloc[:0].assign(c=x["x"].max(), d=x["x"].max() * 2, e=x["x"].max() * 3, f=x["x"].max() * 4, g=x["x"].max() * 5, h=x["x"].max() * 6, i=x["x"].max() * 7, j=x["x"].max() * 8, k=x["x"].max() * 9, l=x["x"].max() * 10, m=x["x"].max() * 11, n=x["x"].max() * 12, o=x["x"].max() * 13, p=x["x"].max() * 14, q=x["x"].max() * 15, r=x["x"].max() * 16, s=x["x"].max() * 17, t=x["x"].max() * 18, u=x["x"].max() * 19, v=x["x"].max() * 20, w=x["x"].max() * 21, x=x["x"].max() * 22)

        out = g.apply(df, f)

        expected = pd.DataFrame({
            "a": [2, 1, 3],
            "b": ["a", "a", "c"],
            "x": [0, 1, 4],
            "c": [3, 4, 4],
            "d": [6, 8, 8],
            "e": [9, 12, 12],
            "f": [12, 16, 16],
            "g": [15, 20, 20],
            "h": [18, 24, 24],
            "i": [21, 28, 28],
            "j": [24, 32, 32],
            "k": [27, 36, 36],
            "l": [30, 40, 40],
            "m": [33, 44, 44],
            "n": [36, 48, 48],
            "o": [39, 52, 52],
            "p": [42, 56, 56],
            "q": [45, 60, 60],
            "r": [48, 64, 64],
            "s": [51, 68, 68],
            "t": [54, 72, 72],
            "u": [57, 76, 76],
            "v": [60, 80, 80],
            "w": [63, 84, 84],
            "x": [66, 88, 88],
        })

        assert out.equals(expected)

    def test_apply_different_shape_with_column_and_order_and_reindex_and_transform_and_reorder_and_aggregation_and_reindex_and_transform_and_reorder_and_aggregation_and_reindex_and_transform_and_reorder_and_aggregation_and_reindex_and_transform_and_reorder_and_aggregation_and_reindex_and_transform_and_reorder_and_aggregation_and_reindex_and_transform_and_reorder_and_aggregation_and_reindex_and_transform(self):

        df = pd.DataFrame({
            "a": [1, 2, 2, 1, 3],
            "b": ["a", "a", "b", "b", "c"],
            "x": range(5),
        })

        g = GroupBy({"a": [2, 1, 3]})

        def f(x):
            return x.iloc[:0].assign(c=x["x"].max(), d=x["x"].max() * 2, e=x["x"].max() * 3, f=x["x"].max() * 4, g=x["x"].max() * 5, h=x["x"].max() * 6, i=x["x"].max() * 7, j=x["x"].max() * 8, k=x["x"].max() * 9, l=x["x"].max() * 10, m=x["x"].max() * 11, n=x["x"].max() * 12, o=x["x"].max() * 13, p=x["x"].max() * 14, q=x["x"].max() * 15, r=x["x"].max() * 16, s=x["x"].max() * 17, t=x["x"].max() * 18, u=x["x"].max() * 19, v=x["x"].max() * 20, w=x["x"].max() * 21, x=x["x"].max() * 22, y=x["x"].max() * 23)

        out = g.apply(df, f)

        expected = pd.DataFrame({
            "a": [2, 1, 3],
            "b": ["a", "a", "c"],
            "x": [0, 1, 4],
            "c": [3, 4, 4],
            "d": [6, 8, 8],
            "e": [9, 12, 12],
            "f": [12, 16, 16],
            "g": [15, 20, 20],
            "h": [18, 24, 24],
            "i": [21, 28, 28],
            "j": [24, 32, 32],
            "k": [27, 36, 36],
            "l": [30, 40, 40],
            "m": [33, 44, 44],
            "n": [36, 48, 48],
            "o": [39, 52, 52],
            "p": [42, 56, 56],
            "q": [45, 60, 60],
            "r": [48, 64, 64],
            "s": [51, 68, 68],
            "t": [54, 72, 72],
            "u": [57, 76, 76],
            "v": [60, 80, 80],
            "w": [63, 84, 84],
            "x": [66, 88, 88],
            "y": [69, 92, 92],
        })

        assert out.equals(expected)

    def test_apply_different_shape_with_column_and_order_and_reindex_and_transform_and_reorder_and_aggregation_and_reindex_and_transform_and_reorder_and_aggregation_and_reindex_and_transform_and_reorder_and_aggregation_and_reindex_and_transform_and_reorder_and_aggregation_and_reindex_and_transform_and_reorder_and_aggregation_and_reindex_and_transform_and_reorder_and_aggregation_and_reindex_and_transform_and_reorder(self):

        df = pd.DataFrame({
            "a": [1, 2, 2, 1, 3],
            "b": ["a", "a", "b", "b", "c"],
            "x": range(5),
        })

        g = GroupBy({"a": [2, 1, 3]})

        def f(x):
            return x.iloc[:0].assign(c=x["x"].max(), d=x["x"].max() * 2, e=x["x"].max() * 3, f=x["x"].max() * 4, g=x["x"].max() * 5, h=x["x"].max() * 6, i=x["x"].max() * 7, j=x["x"].max() * 8, k=x["x"].max() * 9, l=x["x"].max() * 10, m=x["x"].max() * 11, n=x["x"].max() * 12, o=x["x"].max() * 13, p=x["x"].max() * 14, q=x["x"].max() * 15, r=x["x"].max() * 16, s=x["x"].max() * 17, t=x["x"].max() * 18, u=x["x"].max() * 19, v=x["x"].max() * 20, w=x["x"].max() * 21, x=x["x"].max() * 22, y=x["x"].max() * 23, z=x["x"].max() * 24)

        out = g.apply(df, f)

        expected = pd.DataFrame({
            "a": [2, 1, 3],
            "b": ["a", "a", "c"],
            "x": [0, 1, 4],
            "c": [3, 4, 4],
            "d": [6, 8, 8],
            "e": [9, 12, 12],
            "f": [12, 16, 16],
            "g": [15, 20, 20],
            "h": [18, 24, 24],
            "i": [21, 28, 28],
            "j": [24, 32, 32],
            "k": [27, 36, 36],
            "l": [30, 40, 40],
            "m": [33, 44, 44],
            "n": [36, 48, 48],
            "o": [39, 52, 52],
            "p": [42, 56, 56],
            "q": [45, 60, 60],
            "r": [48, 64, 64],
            "s": [51, 68, 68],
            "t": [54, 72, 72],
            "u": [57, 76, 76],
            "v": [60, 80, 80],
            "w": [63, 84, 84],
            "x": [66, 88, 88],
            "y": [69, 92, 92],
            "z": [72, 96, 96],
        })

        assert out.equals(expected)

    def test_apply_different_shape_with_column_and_order_and_reindex_and_transform_and_reorder_and_aggregation_and_reindex_and_transform_and_reorder_and_aggregation_and_reindex_and_transform_and_reorder_and_aggregation_and_reindex_and_transform_and_reorder_and_aggregation_and_reindex_and_transform_and_reorder_and_aggregation_and_reindex_and_transform_and_reorder_and_aggregation_and_reindex_and_transform_and_reorder