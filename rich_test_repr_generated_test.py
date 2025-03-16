from typing import Iterable, Tuple, Union

from rich.repr import ReprError, auto, rich_repr

Result = Iterable[Union[Tuple[str], Tuple[str, str], Tuple[str, str, str]]]


def test_auto_repr() -> None:
    @auto
    class Foo:
        def __rich_repr__(self) -> Result:
            yield "foo"
            yield "bar", {"shopping": ["eggs", "ham", "pineapple"]}
            yield "buy", "hand sanitizer"

    foo = Foo()
    assert repr(foo) == "Foo('foo', bar={'shopping': ['eggs', 'ham', 'pineapple']}, buy='hand sanitizer')"
    Foo.__rich_repr__.angular = True  # type: ignore[attr-defined]
    assert repr(foo) == "<Foo 'foo' bar={'shopping': ['eggs', 'ham', 'pineapple']} buy='hand sanitizer'>"


def test_auto() -> None:
    @auto
    class Foo:
        def __init__(self, a: int, b: int, c: int = 5) -> None:
            self.a = a
            self.b = b
            self.c = c

    foo = Foo(1, 2, 3)
    assert repr(foo) == "Foo(1, 2, c=3)"

    bar = Foo(1, 2, 5)
    assert repr(bar) == "Foo(1, 2)"

    @auto(angular=True)
    class Biz:
        def __init__(self, x: int, y: int) -> None:
            self.x = x
            self.y = y

    biz = Biz(1, 2)
    assert repr(biz) == "<Biz 1 2>"

    @auto
    class Baz:
        def __init__(self, n: int) -> None:
            self.n = n

    baz = Baz(3)
    assert repr(baz) == "Baz(3)"


def test_auto_rich_repr_error() -> None:
    class ReprException(Exception):
        pass

    @auto
    class Foo:
        def __init__(self, a: int) -> None:
            raise ReprException("boom")
            self.a = a

    foo = Foo(1)
    try:
        repr(foo)
    except ReprError:
        pass
    else:
        raise AssertionError("expected exception")


def test_rich_repr() -> None:
    @rich_repr
    class Foo:
        def __init__(self, a: int, b: int, c: int = 5) -> None:
            self.a = a
            self.b = b
            self.c = c

    foo = Foo(1, 2, 3)
    assert repr(foo) == "Foo(1, 2, c=3)"

    bar = Foo(1, 2, 5)
    assert repr(bar) == "Foo(1, 2)"

    @rich_repr(angular=True)
    class Biz:
        def __init__(self, x: int, y: int) -> None:
            self.x = x
            self.y = y

    biz = Biz(1, 2)
    assert repr(biz) == "<Biz 1 2>"

    @rich_repr
    class Baz:
        def __init__(self, n: int) -> None:
            self.n = n

    baz = Baz(3)
    assert repr(baz) == "Baz(3)"