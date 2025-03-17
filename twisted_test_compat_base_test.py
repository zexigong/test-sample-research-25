import pytest
from twisted.test_compat import test_compat

def test_iteritems():
    d = {"a": 1, "b": 2}
    assert list(test_compat.iteritems(d)) == [("a", 1), ("b", 2)]

def test_itervalues():
    d = {"a": 1, "b": 2}
    assert list(test_compat.itervalues(d)) == [1, 2]

def test_items():
    d = {"a": 1, "b": 2}
    assert test_compat.items(d) == [("a", 1), ("b", 2)]

def test_currentframe():
    frame = test_compat.currentframe()
    assert frame is not None

def test_execfile(tmp_path):
    filename = tmp_path / "test_execfile.py"
    filename.write_text("x = 42\n")
    globals_dict = {}
    test_compat.execfile(str(filename), globals_dict)
    assert globals_dict["x"] == 42

def test_cmp():
    assert test_compat.cmp(1, 2) == -1
    assert test_compat.cmp(2, 2) == 0
    assert test_compat.cmp(3, 2) == 1

def test_comparable():
    @test_compat.comparable
    class Example:
        def __init__(self, value):
            self.value = value

        def __cmp__(self, other):
            if self.value < other.value:
                return -1
            elif self.value == other.value:
                return 0
            else:
                return 1

    e1 = Example(1)
    e2 = Example(2)
    assert e1 < e2
    assert e1 != e2
    assert e2 > e1

def test_ioType():
    with open(__file__, "rb") as f:
        assert test_compat.ioType(f) == bytes
    with open(__file__, "r") as f:
        assert test_compat.ioType(f) == str

def test_nativeString():
    assert test_compat.nativeString(b"test") == "test"
    assert test_compat.nativeString("test") == "test"
    with pytest.raises(TypeError):
        test_compat.nativeString(123)

def test_matchingString():
    assert test_compat._matchingString("constant", "input") == "constant"
    assert test_compat._matchingString(b"constant", b"input") == b"constant"
    assert test_compat._matchingString("constant", b"input") == b"constant"
    assert test_compat._matchingString(b"constant", "input") == "constant"

def test_reraise():
    try:
        raise ValueError("test")
    except ValueError as e:
        tb = e.__traceback__
        with pytest.raises(ValueError):
            test_compat.reraise(e, tb)

def test_iterbytes():
    b = b"test"
    assert list(test_compat.iterbytes(b)) == [b"t", b"e", b"s", b"t"]

def test_intToBytes():
    assert test_compat.intToBytes(123) == b"123"

def test_lazyByteSlice():
    b = b"abcdef"
    assert bytes(test_compat.lazyByteSlice(b, 1, 3)) == b"bc"

def test_networkString():
    assert test_compat.networkString("test") == b"test"
    with pytest.raises(TypeError):
        test_compat.networkString(b"test")

def test_bytesEnviron(monkeypatch):
    monkeypatch.setattr("os.environ", {"key": "value"})
    environ = test_compat.bytesEnviron()
    assert environ == {b"key": b"value"}