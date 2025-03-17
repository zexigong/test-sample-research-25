import pytest
from rich.test_repr.test_repr import auto, ReprError, Result

# Dummy class to test the auto decorator
@auto
class Dummy:
    def __init__(self, a, b, c=None):
        self.a = a
        self.b = b
        self.c = c

    def __rich_repr__(self) -> Result:
        yield "a", self.a
        yield "b", self.b
        if self.c is not None:
            yield "c", self.c

def test_auto_decorator_standard_repr():
    obj = Dummy(1, 2, c=3)
    expected_repr = "Dummy(a=1, b=2, c=3)"
    assert repr(obj) == expected_repr

def test_auto_decorator_default_values():
    obj = Dummy(1, 2)
    expected_repr = "Dummy(a=1, b=2)"
    assert repr(obj) == expected_repr

def test_auto_decorator_with_angular():
    @auto(angular=True)
    class AngularDummy:
        def __init__(self, x, y, z=None):
            self.x = x
            self.y = y
            self.z = z

        def __rich_repr__(self) -> Result:
            yield "x", self.x
            yield "y", self.y
            if self.z is not None:
                yield "z", self.z

    obj = AngularDummy(4, 5)
    expected_repr = "<AngularDummy x=4 y=5>"
    assert repr(obj) == expected_repr

def test_rich_repr_error_handling():
    class Broken:
        def __init__(self):
            raise ValueError("This should not happen")

    with pytest.raises(ReprError):
        auto(Broken)

def test_auto_decorator_without_rich_repr():
    @auto
    class NoRichRepr:
        def __init__(self, m, n):
            self.m = m
            self.n = n

    obj = NoRichRepr(7, 8)
    expected_repr = "NoRichRepr(m=7, n=8)"
    assert repr(obj) == expected_repr

def test_auto_decorator_positional_only():
    class PositionalOnly:
        @auto
        def __init__(self, x, /, y):
            self.x = x
            self.y = y

    obj = PositionalOnly(10, 20)
    expected_repr = "PositionalOnly(10, y=20)"
    assert repr(obj) == expected_repr