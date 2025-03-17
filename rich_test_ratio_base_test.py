import pytest
from fractions import Fraction
from typing import Optional, List
from dataclasses import dataclass

# Assuming the source code is in a file named `ratio.py`
from ratio import ratio_resolve, ratio_reduce, ratio_distribute, Edge

@dataclass
class E:
    size: Optional[int] = None
    ratio: int = 1
    minimum_size: int = 1

# Test for ratio_resolve function
def test_ratio_resolve_basic():
    edges = [E(None, 1, 1), E(None, 1, 1), E(None, 1, 1)]
    result = ratio_resolve(110, edges)
    assert sum(result) == 110
    assert all(isinstance(x, int) for x in result)

def test_ratio_resolve_with_fixed_sizes():
    edges = [E(30, 1, 1), E(None, 1, 1), E(None, 1, 1)]
    result = ratio_resolve(110, edges)
    assert sum(result) == 110
    assert result[0] == 30

def test_ratio_resolve_with_minimum_sizes():
    edges = [E(None, 1, 50), E(None, 1, 50), E(None, 1, 1)]
    result = ratio_resolve(110, edges)
    assert sum(result) >= 110
    assert result[0] >= 50
    assert result[1] >= 50

# Test for ratio_reduce function
def test_ratio_reduce_basic():
    ratios = [1, 1, 1]
    maximums = [50, 50, 50]
    values = [0, 0, 0]
    result = ratio_reduce(90, ratios, maximums, values)
    assert sum(result) == 90
    assert all(x <= max_val for x, max_val in zip(result, maximums))

def test_ratio_reduce_with_zero_ratios():
    ratios = [0, 0, 0]
    maximums = [50, 50, 50]
    values = [0, 0, 0]
    result = ratio_reduce(90, ratios, maximums, values)
    assert result == values

# Test for ratio_distribute function
def test_ratio_distribute_basic():
    ratios = [1, 1, 1]
    result = ratio_distribute(90, ratios)
    assert sum(result) == 90
    assert all(isinstance(x, int) for x in result)

def test_ratio_distribute_with_minimums():
    ratios = [1, 1, 1]
    minimums = [20, 20, 20]
    result = ratio_distribute(90, ratios, minimums)
    assert sum(result) == 90
    assert result[0] >= 20
    assert result[1] >= 20
    assert result[2] >= 20

def test_ratio_distribute_no_ratios():
    with pytest.raises(AssertionError):
        ratio_distribute(90, [0, 0, 0])

if __name__ == "__main__":
    pytest.main()