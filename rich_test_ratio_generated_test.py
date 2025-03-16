from typing import Optional

from rich._ratio import ratio_distribute, ratio_reduce, ratio_resolve


class Edge:
    def __init__(self, size: Optional[int], ratio: int = 1, minimum_size: int = 1):
        self.size = size
        self.ratio = ratio
        self.minimum_size = minimum_size

    def __repr__(self) -> str:
        return f"Edge({self.size}, {self.ratio}, {self.minimum_size})"


def test_ratio_resolve() -> None:
    result = ratio_resolve(
        110,
        [
            Edge(None, 1, 1),
            Edge(None, 1, 1),
            Edge(None, 1, 1),
        ],
    )
    assert result == [37, 36, 37]
    assert sum(result) == 110


def test_ratio_resolve_with_sizes() -> None:
    result = ratio_resolve(
        110,
        [
            Edge(20, 1, 1),
            Edge(None, 1, 1),
            Edge(None, 1, 1),
        ],
    )
    assert result == [20, 45, 45]
    assert sum(result) == 110


def test_ratio_resolve_with_minimum_size() -> None:
    result = ratio_resolve(
        110,
        [
            Edge(20, 1, 1),
            Edge(None, 1, 50),
            Edge(None, 1, 1),
        ],
    )
    assert result == [20, 50, 40]
    assert sum(result) == 110


def test_ratio_resolve_with_minimum_size_overflow() -> None:
    result = ratio_resolve(
        20,
        [
            Edge(None, 1, 50),
            Edge(None, 1, 1),
        ],
    )
    assert result == [50, 1]
    assert sum(result) == 51


def test_ratio_resolve_with_different_ratios() -> None:
    result = ratio_resolve(
        110,
        [
            Edge(None, 1, 1),
            Edge(None, 1, 1),
            Edge(None, 2, 1),
        ],
    )
    assert result == [27, 27, 56]
    assert sum(result) == 110


def test_ratio_resolve_with_all_sizes() -> None:
    result = ratio_resolve(
        110,
        [
            Edge(10, 1, 1),
            Edge(10, 1, 1),
            Edge(10, 1, 1),
            Edge(10, 1, 1),
        ],
    )
    assert result == [10, 10, 10, 10]
    assert sum(result) == 40


def test_ratio_resolve_with_zero_ration() -> None:
    result = ratio_resolve(
        110,
        [
            Edge(10, 0, 1),
            Edge(10, 0, 1),
            Edge(None, 1, 1),
            Edge(None, 1, 1),
            Edge(None, 1, 1),
        ],
    )
    assert result == [10, 10, 30, 30, 30]
    assert sum(result) == 110


def test_ratio_resolve_with_zero_minimums() -> None:
    result = ratio_resolve(
        110,
        [
            Edge(10, 0, 1),
            Edge(10, 0, 0),
            Edge(None, 1, 1),
            Edge(None, 1, 0),
            Edge(None, 1, 1),
        ],
    )
    assert result == [10, 10, 30, 30, 30]
    assert sum(result) == 110


def test_ratio_distribute() -> None:
    result = ratio_distribute(110, [1, 1, 1])
    assert result == [37, 36, 37]
    assert sum(result) == 110


def test_ratio_distribute_with_minimums() -> None:
    result = ratio_distribute(110, [1, 1, 1], [50, 1, 1])
    assert result == [50, 30, 30]
    assert sum(result) == 110


def test_ratio_reduce() -> None:
    result = ratio_reduce(110, [1, 1, 1], [10, 10, 10], [20, 20, 20])
    assert result == [10, 10, 10]
    assert sum(result) == 30