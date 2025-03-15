# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

"""
Tests for L{twisted.compat}.
"""

import os
import platform
import socket
import sys
from functools import reduce
from io import BytesIO, IOBase, StringIO, TextIOBase
from types import MethodType
from typing import List, Optional, Tuple, Type, Union
from unittest import skipIf

from incremental import Version

from twisted.python import compat, deprecate
from twisted.python.deprecate import _fullyQualifiedName
from twisted.trial import unittest
from twisted.trial.unittest import FailTest


class OldStyle:
    pass


class NewStyle(object):
    pass


class CompatibleTests(unittest.SynchronousTestCase):
    """
    Tests for backwards compatibility of various Python features.
    """

    def test_classType(self) -> None:
        """
        The old C{types.ClassType} refers to C{type} in Python 3.
        """
        self.assertIs(type, type)

    def test_instanceType(self) -> None:
        """
        The old C{types.InstanceType} refers to C{object} in Python 3.
        """
        self.assertIs(object, compat.InstanceType)

    def test_nativeStringIO(self) -> None:
        """
        The old C{cStringIO.StringIO} refers to C{io.StringIO} in Python 3.
        """
        self.assertIs(StringIO, compat.NativeStringIO)

    def test_frozenset(self) -> None:
        """
        The old C{new.frozenset} refers to C{frozenset} in Python 3.
        """
        self.assertIs(frozenset, compat.frozenset)

    def test_reduce(self) -> None:
        """
        The old C{reduce} refers to C{functools.reduce} in Python 3.
        """
        self.assertIs(reduce, compat.reduce)

    def test_set(self) -> None:
        """
        The old C{new.set} refers to C{set} in Python 3.
        """
        self.assertIs(set, compat.set)

    def test_zip(self) -> None:
        """
        The old C{itertools.izip} refers to C{zip} in Python 3.
        """
        self.assertIs(zip, compat.izip)

    def test_range(self) -> None:
        """
        The old C{xrange} refers to C{range} in Python 3.
        """
        self.assertIs(range, compat.xrange)

    def test_long(self) -> None:
        """
        The old C{types.LongType} refers to C{int} in Python 3.
        """
        self.assertIs(int, compat.long)

    def test_string(self) -> None:
        """
        The old C{types.StringType} refers to C{str} in Python 3.
        """
        self.assertIs(str, compat.StringType)

    def test_unicode(self) -> None:
        """
        The old C{types.UnicodeType} refers to C{str} in Python 3.
        """
        self.assertIs(str, compat.unicode)

    def test_unichr(self) -> None:
        """
        The old C{unichr} refers to C{chr} in Python 3.
        """
        self.assertIs(chr, compat.unichr)

    def test_input(self) -> None:
        """
        The old C{raw_input} refers to C{input} in Python 3.
        """
        self.assertIs(input, compat.raw_input)

    def test_currentframe(self) -> None:
        """
        L{compat.currentframe} calls L{inspect.currentframe} and returns the
        frame object n levels up the stack from the caller.
        """
        import inspect

        f = compat.currentframe(1)
        assert f is not None
        f = f.f_back
        assert f is not None
        self.assertEqual(f.f_code, inspect.currentframe().__code__)

    def test_execfile(self) -> None:
        """
        L{compat.execfile} executes a Python script in the given namespaces.
        """
        filename = self.mktemp()
        with open(filename, "w") as f:
            f.write("foo = 1\n")

        ns: dict = {}
        compat.execfile(filename, ns)

        self.assertIn("foo", ns)
        self.assertEqual(ns["foo"], 1)

    def test_cmp(self) -> None:
        """
        L{compat.cmp} compares two objects and returns a negative number if the
        first is smaller, a positive number if the second is smaller, or zero
        if they are equal.
        """
        self.assertEqual(compat.cmp(1, 1), 0)
        self.assertEqual(compat.cmp(1, 2), -1)
        self.assertEqual(compat.cmp(2, 1), 1)

    def test_comparable(self) -> None:
        """
        L{compat.comparable} is a decorator that ensures support for the
        special C{__cmp__} method, adding C{__eq__}, C{__lt__}, etc. methods to
        the class.
        """
        self._comparableTestHelper(compat.comparable)

    def _comparableTestHelper(self, comparable):
        @comparable
        class Comparable:
            def __init__(self, value):
                self.value = value

            def __cmp__(self, other):
                return compat.cmp(self.value, other.value)

        comparable1 = Comparable(1)
        comparable2 = Comparable(2)
        comparable3 = Comparable(1)

        self.assertTrue(comparable1 == comparable3)
        self.assertFalse(comparable1 != comparable3)
        self.assertFalse(comparable1 == comparable2)
        self.assertTrue(comparable1 != comparable2)

        self.assertTrue(comparable1 < comparable2)
        self.assertTrue(comparable1 <= comparable3)
        self.assertTrue(comparable1 <= comparable2)
        self.assertFalse(comparable1 > comparable2)
        self.assertTrue(comparable1 >= comparable3)
        self.assertFalse(comparable1 >= comparable2)

    def test_ioType(self) -> None:
        """
        L{compat.ioType} determines the type which will be returned from the
        given file-like object's C{read} method and accepted by its C{write}
        method as an argument.
        """
        self.assertIs(compat.ioType(TextIOBase()), str)
        self.assertIs(compat.ioType(IOBase()), bytes)

    def test_nativeString(self) -> None:
        """
        L{compat.nativeString} converts bytes or str to str type, using ASCII
        encoding if conversion is necessary.
        """
        self.assertEqual(compat.nativeString(b"foo"), "foo")
        self.assertEqual(compat.nativeString("foo"), "foo")

        self.assertRaises(TypeError, compat.nativeString, 1)
        self.assertRaises(UnicodeEncodeError, compat.nativeString, "f\x8f\x8f")

    def test_matchingString(self) -> None:
        """
        L{compat._matchingString} converts a constant string (either bytes or
        str) to the same type as the input string, using ASCII encoding if
        conversion is necessary.
        """
        self.assertEqual(compat._matchingString(b"foo", b"foo"), b"foo")
        self.assertEqual(compat._matchingString("foo", "foo"), "foo")
        self.assertEqual(compat._matchingString(b"foo", "foo"), "foo")
        self.assertEqual(compat._matchingString("foo", b"foo"), b"foo")

    def test_reraise(self) -> None:
        """
        L{compat.reraise} re-raises the given exception instance with an
        optional traceback.
        """
        exc = Exception("foo")
        exc.__traceback__ = object()  # type: ignore[assignment]
        tb = exc.__traceback__

        with self.assertRaises(Exception) as ctx:
            compat.reraise(exc, None)

        self.assertIs(ctx.exception, exc)
        self.assertEqual(ctx.exception.__traceback__, tb)

    def test_iterbytes(self) -> None:
        """
        L{compat.iterbytes} returns an iterable wrapper for a C{bytes} object
        that provides the behavior of iterating over C{bytes} on Python 2.
        """
        self.assertEqual(list(compat.iterbytes(b"foo")), [b"f", b"o", b"o"])

    def test_intToBytes(self) -> None:
        """
        L{compat.intToBytes} converts the given integer into C{bytes}, as
        ASCII-encoded Arab numeral.
        """
        self.assertEqual(compat.intToBytes(1), b"1")
        self.assertEqual(compat.intToBytes(123), b"123")

    def test_lazyByteSlice(self) -> None:
        """
        L{compat.lazyByteSlice} returns a memory view of the given bytes-like
        object.
        """
        view = compat.lazyByteSlice(b"foo", 1, 2)
        self.assertEqual(view.tobytes(), b"o")

    def test_networkString(self) -> None:
        """
        L{compat.networkString} converts a string to C{bytes} using ASCII
        encoding.
        """
        self.assertEqual(compat.networkString("foo"), b"foo")
        self.assertRaises(UnicodeEncodeError, compat.networkString, "f\x8f\x8f")

    def test_bytesEnviron(self) -> None:
        """
        L{compat.bytesEnviron} returns a L{dict} of L{os.environ} where all
        text-strings are encoded into L{bytes}.
        """
        environ = {b"foo": b"bar"}
        with unittest.TestCase.patch(self, "os.environ", environ):
            self.assertEqual(compat.bytesEnviron(), environ)

    def test_constructMethod(self) -> None:
        """
        L{compat._constructMethod} returns a bound method.
        """
        method = compat._constructMethod(str, "lower", "FOO")
        self.assertIsInstance(method, MethodType)
        self.assertEqual(method(), "foo")


class IterItemsTests(unittest.SynchronousTestCase):
    """
    Tests for L{compat.iteritems}.
    """

    def test_deprecation(self) -> None:
        """
        L{compat.iteritems} is deprecated.
        """
        self.callDeprecated(
            (Version("Twisted", 21, 2, 0), "Use d.items() instead"),
            compat.iteritems,
            {},
        )


class IterValuesTests(unittest.SynchronousTestCase):
    """
    Tests for L{compat.itervalues}.
    """

    def test_deprecation(self) -> None:
        """
        L{compat.itervalues} is deprecated.
        """
        self.callDeprecated(
            (Version("Twisted", 21, 2, 0), "Use d.values() instead"),
            compat.itervalues,
            {},
        )


class ItemsTests(unittest.SynchronousTestCase):
    """
    Tests for L{compat.items}.
    """

    def test_deprecation(self) -> None:
        """
        L{compat.items} is deprecated.
        """
        self.callDeprecated(
            (Version("Twisted", 21, 2, 0), "Use list(d.items()) instead"),
            compat.items,
            {},
        )


class ReraiseTests(unittest.SynchronousTestCase):
    """
    Tests for L{compat.reraise}.
    """

    def test_deprecation(self) -> None:
        """
        L{compat.reraise} is deprecated.
        """
        self.callDeprecated(
            (Version("Twisted", 21, 2, 0), "Use raise exception.with_traceback instead"),
            compat.reraise,
            Exception("foo"),
            None,
        )


class IntToBytesTests(unittest.SynchronousTestCase):
    """
    Tests for L{compat.intToBytes}.
    """

    def test_deprecation(self) -> None:
        """
        L{compat.intToBytes} is deprecated.
        """
        self.callDeprecated(
            (Version("Twisted", 21, 2, 0), "Use b'%d' instead"),
            compat.intToBytes,
            1,
        )


class BytesEnvironTests(unittest.SynchronousTestCase):
    """
    Tests for L{compat.bytesEnviron}.
    """

    def test_deprecation(self) -> None:
        """
        L{compat.bytesEnviron} is deprecated.
        """
        self.callDeprecated(
            (Version("Twisted", 21, 2, 0), "Use os.environb instead"),
            compat.bytesEnviron,
        )


class ReduceTests(unittest.SynchronousTestCase):
    """
    Tests for L{compat.reduce}.
    """

    def test_deprecation(self) -> None:
        """
        L{compat.reduce} is deprecated.
        """
        self.callDeprecated(
            (Version("Twisted", 21, 2, 0), "Use functools.reduce directly"),
            compat.reduce,
            lambda x, y: x + y,
            [1, 2, 3],
        )


class NativeStringIOTests(unittest.SynchronousTestCase):
    """
    Tests for L{compat.NativeStringIO}.
    """

    def test_deprecation(self) -> None:
        """
        L{compat.NativeStringIO} is deprecated.
        """
        self.callDeprecated(
            (Version("Twisted", 21, 2, 0), "Use io.StringIO directly"),
            compat.NativeStringIO,
        )


class UrllibParseTests(unittest.SynchronousTestCase):
    """
    Tests for L{compat.urllib_parse}.
    """

    def test_deprecation(self) -> None:
        """
        L{compat.urllib_parse} is deprecated.
        """
        self.callDeprecated(
            (Version("Twisted", 21, 2, 0), "Import urllib.parse directly"),
            getattr,
            compat,
            "urllib_parse",
        )


class EscapeTests(unittest.SynchronousTestCase):
    """
    Tests for L{compat.escape}.
    """

    def test_deprecation(self) -> None:
        """
        L{compat.escape} is deprecated.
        """
        self.callDeprecated(
            (Version("Twisted", 21, 2, 0), "Use html.escape directly"),
            compat.escape,
            "<",
        )


class UrlQuoteTests(unittest.SynchronousTestCase):
    """
    Tests for L{compat.urlquote}.
    """

    def test_deprecation(self) -> None:
        """
        L{compat.urlquote} is deprecated.
        """
        self.callDeprecated(
            (Version("Twisted", 21, 2, 0), "Use urllib.parse.quote directly"),
            compat.urlquote,
            "foo",
        )


class UrlUnquoteTests(unittest.SynchronousTestCase):
    """
    Tests for L{compat.urlunquote}.
    """

    def test_deprecation(self) -> None:
        """
        L{compat.urlunquote} is deprecated.
        """
        self.callDeprecated(
            (Version("Twisted", 21, 2, 0), "Use urllib.parse.unquote directly"),
            compat.urlunquote,
            "foo",
        )


class CookieLibTests(unittest.SynchronousTestCase):
    """
    Tests for L{compat.cookielib}.
    """

    def test_deprecation(self) -> None:
        """
        L{compat.cookielib} is deprecated.
        """
        self.callDeprecated(
            (Version("Twisted", 21, 2, 0), "Use http.cookiejar directly"),
            getattr,
            compat,
            "cookielib",
        )


class InternTests(unittest.SynchronousTestCase):
    """
    Tests for L{compat.intern}.
    """

    def test_deprecation(self) -> None:
        """
        L{compat.intern} is deprecated.
        """
        self.callDeprecated(
            (Version("Twisted", 21, 2, 0), "Use sys.intern directly"),
            compat.intern,
            "foo",
        )


class SequenceTests(unittest.SynchronousTestCase):
    """
    Tests for L{compat.Sequence}.
    """

    def test_deprecation(self) -> None:
        """
        L{compat.Sequence} is deprecated.
        """
        self.callDeprecated(
            (Version("Twisted", 21, 2, 0), "Use collections.abc.Sequence directly"),
            getattr,
            compat,
            "Sequence",
        )


class FileTypeTests(unittest.SynchronousTestCase):
    """
    Tests for L{compat.FileType}.
    """

    def test_deprecation(self) -> None:
        """
        L{compat.FileType} is deprecated.
        """
        self.callDeprecated(
            (Version("Twisted", 21, 2, 0), "Obsolete alias for io.IOBase"),
            getattr,
            compat,
            "FileType",
        )


class FrozensetTests(unittest.SynchronousTestCase):
    """
    Tests for L{compat.frozenset}.
    """

    def test_deprecation(self) -> None:
        """
        L{compat.frozenset} is deprecated.
        """
        self.callDeprecated(
            (Version("Twisted", 21, 2, 0), "Obsolete alias for frozenset builtin type"),
            getattr,
            compat,
            "frozenset",
        )


class InstanceTypeTests(unittest.SynchronousTestCase):
    """
    Tests for L{compat.InstanceType}.
    """

    def test_deprecation(self) -> None:
        """
        L{compat.InstanceType} is deprecated.
        """
        self.callDeprecated(
            (Version("Twisted", 21, 2, 0), "Old-style classes don't exist in Python 3"),
            getattr,
            compat,
            "InstanceType",
        )


class IzipTests(unittest.SynchronousTestCase):
    """
    Tests for L{compat.izip}.
    """

    def test_deprecation(self) -> None:
        """
        L{compat.izip} is deprecated.
        """
        self.callDeprecated(
            (Version("Twisted", 21, 2, 0), "Obsolete alias for zip() builtin"),
            getattr,
            compat,
            "izip",
        )


class LongTests(unittest.SynchronousTestCase):
    """
    Tests for L{compat.long}.
    """

    def test_deprecation(self) -> None:
        """
        L{compat.long} is deprecated.
        """
        self.callDeprecated(
            (Version("Twisted", 21, 2, 0), "Obsolete alias for int builtin type"),
            getattr,
            compat,
            "long",
        )


class RangeTests(unittest.SynchronousTestCase):
    """
    Tests for L{compat.range}.
    """

    def test_deprecation(self) -> None:
        """
        L{compat.range} is deprecated.
        """
        self.callDeprecated(
            (Version("Twisted", 21, 2, 0), "Obsolete alias for range() builtin"),
            getattr,
            compat,
            "range",
        )


class RawInputTests(unittest.SynchronousTestCase):
    """
    Tests for L{compat.raw_input}.
    """

    def test_deprecation(self) -> None:
        """
        L{compat.raw_input} is deprecated.
        """
        self.callDeprecated(
            (Version("Twisted", 21, 2, 0), "Obsolete alias for input() builtin"),
            getattr,
            compat,
            "raw_input",
        )


class SetTests(unittest.SynchronousTestCase):
    """
    Tests for L{compat.set}.
    """

    def test_deprecation(self) -> None:
        """
        L{compat.set} is deprecated.
        """
        self.callDeprecated(
            (Version("Twisted", 21, 2, 0), "Obsolete alias for set builtin type"),
            getattr,
            compat,
            "set",
        )


class StringTypeTests(unittest.SynchronousTestCase):
    """
    Tests for L{compat.StringType}.
    """

    def test_deprecation(self) -> None:
        """
        L{compat.StringType} is deprecated.
        """
        self.callDeprecated(
            (Version("Twisted", 21, 2, 0), "Obsolete alias for str builtin type"),
            getattr,
            compat,
            "StringType",
        )


class UnichrTests(unittest.SynchronousTestCase):
    """
    Tests for L{compat.unichr}.
    """

    def test_deprecation(self) -> None:
        """
        L{compat.unichr} is deprecated.
        """
        self.callDeprecated(
            (Version("Twisted", 21, 2, 0), "Obsolete alias for chr() builtin"),
            getattr,
            compat,
            "unichr",
        )


class UnicodeTests(unittest.SynchronousTestCase):
    """
    Tests for L{compat.unicode}.
    """

    def test_deprecation(self) -> None:
        """
        L{compat.unicode} is deprecated.
        """
        self.callDeprecated(
            (Version("Twisted", 21, 2, 0), "Obsolete alias for str builtin type"),
            getattr,
            compat,
            "unicode",
        )


class XrangeTests(unittest.SynchronousTestCase):
    """
    Tests for L{compat.xrange}.
    """

    def test_deprecation(self) -> None:
        """
        L{compat.xrange} is deprecated.
        """
        self.callDeprecated(
            (Version("Twisted", 21, 2, 0), "Obsolete alias for range() builtin"),
            getattr,
            compat,
            "xrange",
        )


@skipIf(
    platform.python_implementation() != "PyPy",
    "Test only makes sense on PyPy.",
)
class PyPy3BlockingHackTests(unittest.TestCase):
    """
    Tests for L{twisted.compat._pypy3BlockingHack}.
    """

    def patch(self, obj, attribute, value):
        """
        Override so that we can also patch builtins.
        """
        original = getattr(obj, attribute, None)

        def cleanup():
            if original is None:
                delattr(obj, attribute)
            else:
                setattr(obj, attribute, original)

        self.addCleanup(cleanup)
        setattr(obj, attribute, value)

    def test_socketFromFD(self) -> None:
        """
        L{twisted.compat._pypy3BlockingHack} replaces C{socket.fromfd} with a
        more conservative version.
        """
        from fcntl import F_GETFL, F_SETFL, fcntl

        def fakeFromFD(fd, family, type, proto=None):
            pass

        self.patch(socket, "fromfd", fakeFromFD)

        def fakeFcntl(fd, cmd, flags=0):
            return 0

        self.patch("fcntl.fcntl", fakeFcntl)

        compat._pypy3BlockingHack()

        self.assertIsNot(socket.fromfd, fakeFromFD)

    def test_socketFromFDWithoutFcntl(self) -> None:
        """
        L{twisted.compat._pypy3BlockingHack} does nothing if C{fcntl.fcntl}
        can't be imported.
        """
        from fcntl import F_GETFL, F_SETFL, fcntl

        self.patch("fcntl.fcntl", None)

        def fakeFromFD(fd, family, type, proto=None):
            pass

        self.patch(socket, "fromfd", fakeFromFD)
        compat._pypy3BlockingHack()
        self.assertIs(socket.fromfd, fakeFromFD)

    def test_socketFromFDWithoutFcntlConstants(self) -> None:
        """
        L{twisted.compat._pypy3BlockingHack} does nothing if C{fcntl.fcntl}
        constants can't be imported.
        """
        self.patch("fcntl.F_GETFL", None)
        self.patch("fcntl.F_SETFL", None)
        self.patch("fcntl.fcntl", None)

        def fakeFromFD(fd, family, type, proto=None):
            pass

        self.patch(socket, "fromfd", fakeFromFD)
        compat._pypy3BlockingHack()
        self.assertIs(socket.fromfd, fakeFromFD)

    def test_socketFromFDOnCPython(self) -> None:
        """
        L{twisted.compat._pypy3BlockingHack} does nothing if the platform is
        not PyPy.
        """
        self.patch(compat, "_PYPY", False)

        def fakeFromFD(fd, family, type, proto=None):
            pass

        self.patch(socket, "fromfd", fakeFromFD)
        compat._pypy3BlockingHack()
        self.assertIs(socket.fromfd, fakeFromFD)

    def test_socketFromFDAlreadyFixed(self) -> None:
        """
        L{twisted.compat._pypy3BlockingHack} does nothing if
        C{socket.fromfd}'s name is the same as the fixed name.
        """
        from fcntl import F_GETFL, F_SETFL, fcntl

        def fakeFromFD(fd, family, type, proto=None):
            pass

        fakeFromFD.__name__ = "fromFDWithoutModifyingFlags"
        self.patch(socket, "fromfd", fakeFromFD)
        compat._pypy3BlockingHack()
        self.assertIs(socket.fromfd, fakeFromFD)