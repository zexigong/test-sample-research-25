# -*- test-case-name: twisted.test.test_formmethod -*-
# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

"""
Tests for L{twisted.python.formmethod}.
"""

from twisted.trial import unittest
from twisted.python import formmethod


class InputTests(unittest.TestCase):
    def test_string(self):
        s = formmethod.String("foo")
        s.coerce("bar")

    def test_hidden(self):
        h = formmethod.Hidden("foo")
        h.coerce("bar")

    def test_hiddenWithDefault(self):
        h = formmethod.Hidden("foo", default="bar")
        h.coerce(None)

    def test_integer(self):
        i = formmethod.Integer("foo")
        self.assertEqual(1, i.coerce("1"))
        self.assertRaises(formmethod.InputError, i.coerce, "bar")
        self.assertRaises(formmethod.InputError, i.coerce, "1.1")
        self.assertRaises(formmethod.InputError, i.coerce, "")

    def test_integerNotNone(self):
        i = formmethod.Integer("foo", allowNone=0)
        self.assertEqual(1, i.coerce("1"))
        self.assertRaises(formmethod.InputError, i.coerce, "bar")
        self.assertRaises(formmethod.InputError, i.coerce, "1.1")
        self.assertRaises(formmethod.InputError, i.coerce, "")
        self.assertRaises(formmethod.InputError, i.coerce, None)

    def test_flags(self):
        f = formmethod.Flags(
            "foo",
            flags=[("1", "a", ""), ("2", "b", ""), ("3", "c", "")],
            default=["a", "b"],
        )
        self.assertEqual(["a", "b"], f.coerce(["1", "2"]))
        self.assertEqual(["c"], f.coerce(["3"]))
        self.assertEqual(["a", "c"], f.coerce(["1", "3"]))
        self.assertRaises(formmethod.InputError, f.coerce, ["foo"])

    def test_flagsAllowNone(self):
        f = formmethod.Flags(
            "foo",
            flags=[("1", "a", ""), ("2", "b", ""), ("3", "c", "")],
            default=["a", "b"],
            allowNone=0,
        )
        self.assertEqual(["a", "b"], f.coerce(["1", "2"]))
        self.assertEqual(["c"], f.coerce(["3"]))
        self.assertEqual(["a", "c"], f.coerce(["1", "3"]))
        self.assertRaises(formmethod.InputError, f.coerce, ["foo"])

    def test_flagsDisallowNone(self):
        f = formmethod.Flags(
            "foo",
            flags=[("1", "a", ""), ("2", "b", ""), ("3", "c", "")],
            default=["a", "b"],
            allowNone=0,
        )
        self.assertEqual([], f.coerce([]))
        self.assertEqual([], f.coerce(None))

    def test_flagsAllowNoneDefault(self):
        f = formmethod.Flags(
            "foo",
            flags=[("1", "a", ""), ("2", "b", ""), ("3", "c", "")],
            default=["a", "b"],
            allowNone=1,
        )
        self.assertIsNone(f.coerce(None))

    def test_flagsAllowNoneEmpty(self):
        f = formmethod.Flags(
            "foo",
            flags=[("1", "a", ""), ("2", "b", ""), ("3", "c", "")],
            default=["a", "b"],
            allowNone=1,
        )
        self.assertIsNone(f.coerce([]))


class MethodTests(unittest.TestCase):
    def setUp(self):
        self.s = formmethod.MethodSignature(
            formmethod.String("s"),
            formmethod.Integer("i"),
            formmethod.Flags(
                "f", flags=[("1", "a", ""), ("2", "b", ""), ("3", "c", "")]
            ),
            formmethod.CheckGroup(
                "c", flags=[("1", "a", ""), ("2", "b", ""), ("3", "c", "")]
            ),
            formmethod.File("file"),
        )

    def test_getArgs(self):
        fm = self.s.method(lambda: None)
        args = fm.getArgs()
        self.assertEqual(len(args), 5)

        self.assertEqual(args[0].name, "s")
        self.assertEqual(args[1].name, "i")
        self.assertEqual(args[2].name, "f")
        self.assertEqual(args[3].name, "c")
        self.assertEqual(args[4].name, "file")