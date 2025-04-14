# -*- test-case-name: twisted.test_compat.test_compat -*-
#
# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

import os
import unittest
from io import BytesIO, StringIO
from twisted.test.compat import (
    iteritems,
    itervalues,
    items,
    currentframe,
    execfile,
    cmp,
    comparable,
    ioType,
    nativeString,
    _matchingString,
    reraise,
    iterbytes,
    intToBytes,
    lazyByteSlice,
    networkString,
    bytesEnviron,
    _constructMethod,
)

class CompatibilityTests(unittest.TestCase):
    def test_iteritems(self):
        d = {'a': 1, 'b': 2}
        self.assertEqual(list(iteritems(d)), list(d.items()))

    def test_itervalues(self):
        d = {'a': 1, 'b': 2}
        self.assertEqual(list(itervalues(d)), list(d.values()))

    def test_items(self):
        d = {'a': 1, 'b': 2}
        self.assertEqual(items(d), list(d.items()))

    def test_currentframe(self):
        f = currentframe(0)
        self.assertTrue(f)

    def test_execfile(self):
        globals = {}
        locals = {}
        script = "x = 42\n"
        filename = "test_execfile.py"
        with open(filename, "w") as f:
            f.write(script)
        
        try:
            execfile(filename, globals, locals)
            self.assertEqual(locals['x'], 42)
        finally:
            os.remove(filename)

    def test_cmp(self):
        self.assertEqual(cmp(1, 2), -1)
        self.assertEqual(cmp(2, 2), 0)
        self.assertEqual(cmp(3, 2), 1)

    def test_comparable(self):
        @comparable
        class ComparableExample:
            def __init__(self, value):
                self.value = value

            def __cmp__(self, other):
                if not isinstance(other, ComparableExample):
                    return NotImplemented
                return cmp(self.value, other.value)

        a = ComparableExample(1)
        b = ComparableExample(2)

        self.assertTrue(a < b)
        self.assertTrue(b > a)
        self.assertFalse(a == b)

    def test_ioType_textIO(self):
        self.assertEqual(ioType(StringIO()), str)

    def test_ioType_bytesIO(self):
        self.assertEqual(ioType(BytesIO()), bytes)

    def test_nativeString(self):
        self.assertEqual(nativeString(b"hello"), "hello")
        self.assertEqual(nativeString("hello"), "hello")

    def test_matchingString(self):
        self.assertEqual(_matchingString("constant", b"input"), b"constant")
        self.assertEqual(_matchingString(b"constant", "input"), "constant")

    def test_reraise(self):
        try:
            raise ValueError("Test")
        except ValueError as e:
            try:
                reraise(e, e.__traceback__)
            except ValueError as re_raised:
                self.assertEqual(str(re_raised), "Test")

    def test_iterbytes(self):
        b = b"abc"
        self.assertEqual(list(iterbytes(b)), [b"a", b"b", b"c"])

    def test_intToBytes(self):
        self.assertEqual(intToBytes(123), b"123")

    def test_lazyByteSlice(self):
        b = b"abcdef"
        self.assertEqual(lazyByteSlice(b, 2, 3).tobytes(), b"cde")
        self.assertEqual(lazyByteSlice(b, 4).tobytes(), b"ef")

    def test_networkString(self):
        self.assertEqual(networkString("hello"), b"hello")

    def test_bytesEnviron(self):
        if os.name == 'posix':
            environ = bytesEnviron()
            self.assertIsInstance(environ, dict)
            for key, value in environ.items():
                self.assertIsInstance(key, bytes)
                self.assertIsInstance(value, bytes)

    def test_constructMethod(self):
        class TestClass:
            def method(self):
                return "result"

        instance = TestClass()
        method = _constructMethod(TestClass, "method", instance)
        self.assertEqual(method(), "result")