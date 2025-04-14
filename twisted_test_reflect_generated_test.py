# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

"""
Tests for L{twisted.python.reflect}.
"""

import gc
import os
import re
import sys
import types
import weakref
from importlib import import_module
from types import ModuleType
from typing import Dict, List, Tuple

from twisted.python import reflect
from twisted.python.compat import execfile
from twisted.python.filepath import FilePath
from twisted.python.reflect import namedAny, namedModule, requireModule
from twisted.python.versions import Version
from twisted.trial import unittest


class PrefixedMethods(unittest.SynchronousTestCase):
    def test_prefixedMethods(self):
        """
        L{reflect.prefixedMethods} collects all methods of a given object with
        a given prefix.
        """

        class Test:
            def abc_1(self):
                pass

            def abc_2(self):
                pass

            def xyz_1(self):
                pass

            def xyz_2(self):
                pass

        o = Test()
        y = reflect.prefixedMethods(o, "abc_")
        self.assertEqual(len(y), 2)
        for x in y:
            self.assertIn(x.__name__, ["abc_1", "abc_2"])
        y = reflect.prefixedMethods(o, "xyz_")
        self.assertEqual(len(y), 2)
        for x in y:
            self.assertIn(x.__name__, ["xyz_1", "xyz_2"])


class TestObjectGrep(unittest.SynchronousTestCase):
    def setUp(self):
        self.cycle = []
        self.cycle.append(self.cycle)

    def test_repr(self):
        """
        Make sure that objgrep can return a repr of a recursive object.
        """
        self.assertIsInstance(reflect.safe_repr(self.cycle), str)

    def test_str(self):
        """
        Make sure that objgrep can return a str of a recursive object.
        """
        self.assertIsInstance(reflect.safe_str(self.cycle), str)

    def test_strNotUnicode(self):
        """
        Make sure that objgrep doesn't return a unicode object when
        handed a utf-8 encoded string on Python 2.
        """
        self.assertIsInstance(reflect.safe_str("test"), str)

    def test_strUnicode(self):
        """
        Make sure that objgrep does return a unicode object when
        handed a unicode object.
        """
        self.assertIsInstance(reflect.safe_str(u"test"), str)

    def test_objgrep(self):
        """
        Make sure that objgrep works.
        """
        l = []
        l.append(l)
        self.assertEqual(
            reflect.objgrep(l, l, reflect.isSame, maxDepth=3),
            ["[0]", "[0][0]", "[0][0][0]"],
        )

    def test_objgrep_empty(self):
        """
        L{objgrep} returns an empty list if the passed object is not found.
        """
        l = []
        l.append(l)
        self.assertEqual(
            reflect.objgrep(l, object(), reflect.isSame, maxDepth=3),
            [],
        )

    def test_objgrep_same(self):
        """
        Make sure that objgrep works with isSame.
        """
        l = []
        l.append(l)
        self.assertEqual(
            reflect.objgrep(l, l, reflect.isSame, maxDepth=3),
            ["[0]", "[0][0]", "[0][0][0]"],
        )

    def test_objgrep_different(self):
        """
        Make sure that objgrep works with isLike.
        """
        l = []
        l.append(l)
        self.assertEqual(
            reflect.objgrep(l, [], reflect.isLike, maxDepth=3),
            ["[0]", "[0][0]", "[0][0][0]"],
        )

    def test_objgrep_isOfType(self):
        """
        Make sure that objgrep works with isOfType.
        """
        l = []
        l.append(l)
        self.assertEqual(
            reflect.objgrep(l, list, reflect.isOfType, maxDepth=3),
            ["", "[0]", "[0][0]", "[0][0][0]"],
        )

    def test_objgrep_noCycles(self):
        """
        L{reflect.objgrep} doesn't loop infinitely on recursive structures.
        """
        l = []
        l.append(l)
        self.assertEqual(
            reflect.objgrep(l, l, reflect.isSame, maxDepth=3),
            ["[0]", "[0][0]", "[0][0][0]"],
        )

    def test_objgrep_weakref(self):
        """
        L{reflect.objgrep} should properly descend into weakrefs, and print
        them as '()' in the resulting path.
        """
        self.assertEqual(
            reflect.objgrep(self.cycle, self.cycle, reflect.isSame, maxDepth=3),
            ["[0]", "[0][0]", "[0][0][0]"],
        )
        w = weakref.ref(self.cycle)
        self.assertEqual(
            reflect.objgrep(w, self.cycle, reflect.isSame, maxDepth=3),
            ["()"],
        )

    def test_objgrep_dict(self):
        """
        L{reflect.objgrep} should print dictionaries with reprs for keys.
        """
        d = {"foo": "bar"}
        self.assertEqual(
            reflect.objgrep(d, "bar", reflect.isLike),
            ["['foo']"],
        )

    def test_objgrep_unknown(self):
        """
        L{reflect.objgrep} should print something when it encounters an unknown
        type.
        """
        obj = object()
        self.assertEqual(
            reflect.objgrep(obj, "hello", reflect.isLike, showUnknowns=1),
            [],
        )


class TestRequireModule(unittest.SynchronousTestCase):
    """
    Tests for L{twisted.python.reflect.requireModule}
    """

    def test_importError(self):
        """
        L{requireModule} returns C{None} if the specified module cannot be
        imported.
        """
        self.assertIsNone(requireModule("invalid_module_name"))

    def test_importErrorDefault(self):
        """
        L{requireModule} returns a user specified default value if the module
        cannot be imported.
        """
        sentinel = object()
        self.assertIs(requireModule("invalid_module_name", sentinel), sentinel)

    def test_importSuccess(self):
        """
        L{requireModule} returns the module object if the module is imported
        successfully.
        """
        self.assertIs(requireModule("sys"), sys)

    def test_importSuccessWithDefault(self):
        """
        L{requireModule} returns the module object if the module is imported
        successfully, even if a default is specified.
        """
        self.assertIs(requireModule("sys", object()), sys)


class TestNamedAny(unittest.SynchronousTestCase):
    """
    Tests for L{twisted.python.reflect.namedAny}
    """

    def test_basicTypes(self):
        """
        Test that the basic types can be retrieved.
        """
        self.assertIs(namedAny("twisted.python.reflect.sys"), sys)
        self.assertIs(namedAny("twisted.python.reflect.sys.version"), sys.version)
        self.assertIs(namedAny("twisted.python.reflect.QueueMethod"), reflect.QueueMethod)

    def test_attributes(self):
        """
        Test that attributes of classes can be retrieved.
        """
        self.assertIs(namedAny("twisted.python.reflect.QueueMethod.__init__"), reflect.QueueMethod.__init__)

    def test_module_class(self):
        """
        Test that a class in a module can be retrieved.
        """
        self.assertIs(namedAny("twisted.python.test.test_reflect.TestNamedAny"), TestNamedAny)

    def test_module_function(self):
        """
        Test that a function in a module can be retrieved.
        """
        self.assertIs(namedAny("twisted.python.reflect.namedAny"), namedAny)

    def test_module_class_method(self):
        """
        Test that a method of a class in a module can be retrieved.
        """
        self.assertIs(namedAny("twisted.python.test.test_reflect.TestNamedAny.test_module_class_method"), self.test_module_class_method)

    def test_module_variable(self):
        """
        Test that a variable in a module can be retrieved.
        """
        self.assertIs(namedAny("twisted.python.reflect.RegexType"), reflect.RegexType)

    def test_invalid_name(self):
        """
        L{namedAny} raises L{InvalidName} when it is given an invalid name.
        """
        self.assertRaises(reflect.InvalidName, namedAny, "")
        self.assertRaises(reflect.InvalidName, namedAny, ".")
        self.assertRaises(reflect.InvalidName, namedAny, "sys.version.")
        self.assertRaises(reflect.InvalidName, namedAny, "sys..version")
        self.assertRaises(reflect.InvalidName, namedAny, "invalid_module_name")

    def test_module_not_found(self):
        """
        L{namedAny} raises L{ModuleNotFound} when the specified module cannot
        be found.
        """
        self.assertRaises(reflect.ModuleNotFound, namedAny, "invalid_module_name.version")

    def test_object_not_found(self):
        """
        L{namedAny} raises L{ObjectNotFound} when the specified object cannot
        be found.
        """
        self.assertRaises(reflect.ObjectNotFound, namedAny, "sys.invalid_attribute_name")

    def test_attribute_error(self):
        """
        L{namedAny} raises L{AttributeError} when the specified object cannot
        be found.
        """
        self.assertRaises(AttributeError, namedAny, "twisted.python.reflect.QueueMethod.invalid_attribute_name")


class TestFilenameToModuleName(unittest.SynchronousTestCase):
    """
    Tests for L{twisted.python.reflect.filenameToModuleName}.
    """

    def test_filenameToModuleName(self):
        """
        L{reflect.filenameToModuleName} returns the dotted name of a module
        that would be imported if that filename were imported.
        """
        self.assertEqual(
            reflect.filenameToModuleName(os.path.abspath("twisted")),
            "twisted",
        )
        self.assertEqual(
            reflect.filenameToModuleName("twisted"),
            "twisted",
        )
        self.assertEqual(
            reflect.filenameToModuleName("twisted/__init__.py"),
            "twisted",
        )
        self.assertEqual(
            reflect.filenameToModuleName("twisted/test/test_reflect.py"),
            "twisted.test.test_reflect",
        )
        self.assertEqual(
            reflect.filenameToModuleName("twisted/test/test_reflect"),
            "twisted.test.test_reflect",
        )

    def test_filenameToModuleName_unicode(self):
        """
        L{reflect.filenameToModuleName} accepts both C{bytes} and C{unicode}
        filenames on Python 3.
        """
        self.assertEqual(
            reflect.filenameToModuleName(b"twisted/test/test_reflect.py"),
            "twisted.test.test_reflect",
        )
        self.assertEqual(
            reflect.filenameToModuleName(u"twisted/test/test_reflect.py"),
            "twisted.test.test_reflect",
        )


class TestNamedModule(unittest.SynchronousTestCase):
    """
    Tests for L{twisted.python.reflect.namedModule}.
    """

    def test_namedModule(self):
        """
        L{reflect.namedModule} imports and returns the module with the given
        name.
        """
        self.assertIs(namedModule("twisted.python"), import_module("twisted.python"))
        self.assertIs(namedModule("twisted.python.reflect"), import_module("twisted.python.reflect"))


class TestFullyQualifiedName(unittest.SynchronousTestCase):
    """
    Tests for L{twisted.python.reflect.fullyQualifiedName}.
    """

    def test_fullyQualifiedName(self):
        """
        L{reflect.fullyQualifiedName} returns the fully qualified name of a
        module, class, method or function.
        """
        self.assertEqual(reflect.fullyQualifiedName(reflect.fullyQualifiedName), "twisted.python.reflect.fullyQualifiedName")
        self.assertEqual(reflect.fullyQualifiedName(reflect.Reflector), "twisted.python.reflect.Reflector")
        self.assertEqual(reflect.fullyQualifiedName(reflect), "twisted.python.reflect")
        self.assertEqual(reflect.fullyQualifiedName(reflect.fullyQualifiedName.__call__), "twisted.python.reflect.fullyQualifiedName.__call__")


class TestSafeRepr(unittest.SynchronousTestCase):
    """
    Tests for L{twisted.python.reflect.safe_repr}.
    """

    def test_safe_repr(self):
        """
        L{reflect.safe_repr} returns a string representation of an object, or a
        string containing a traceback, if that object's C{__repr__} raised an
        exception.
        """

        class BrokenRepr:
            def __repr__(self):
                1 / 0

        self.assertEqual(
            reflect.safe_repr(BrokenRepr()),
            "<BrokenRepr instance at 0x{:x} with repr error:\n Traceback (most recent call last):\n ZeroDivisionError: division by zero\n>".format(
                id(BrokenRepr())
            ),
        )
        self.assertEqual(
            reflect.safe_repr("foo"),
            repr("foo"),
        )


class TestSafeStr(unittest.SynchronousTestCase):
    """
    Tests for L{twisted.python.reflect.safe_str}.
    """

    def test_safe_str(self):
        """
        L{reflect.safe_str} returns a string representation of an object, or a
        string containing a traceback, if that object's C{__str__} raised an
        exception.
        """

        class BrokenStr:
            def __str__(self):
                1 / 0

        self.assertEqual(
            reflect.safe_str(BrokenStr()),
            "<BrokenStr instance at 0x{:x} with str error:\n Traceback (most recent call last):\n ZeroDivisionError: division by zero\n>".format(
                id(BrokenStr())
            ),
        )
        self.assertEqual(
            reflect.safe_str("foo"),
            str("foo"),
        )


class TestAddMethodNamesToDict(unittest.SynchronousTestCase):
    """
    Tests for L{twisted.python.reflect.addMethodNamesToDict}.
    """

    def test_addMethodNamesToDict(self):
        """
        L{reflect.addMethodNamesToDict} goes through a class and its bases and
        puts method names starting with a given prefix in a given dictionary.
        """

        class A:
            def foo(self):
                pass

        class B(A):
            def bar(self):
                pass

        class C(B):
            def baz(self):
                pass

        d = {}
        reflect.addMethodNamesToDict(C, d, "ba")
        self.assertEqual(d, {"bar": 1, "baz": 1})


class TestAccumulateMethods(unittest.SynchronousTestCase):
    """
    Tests for L{twisted.python.reflect.accumulateMethods}.
    """

    def test_accumulateMethods(self):
        """
        L{reflect.accumulateMethods} goes through a class and its bases and
        adds all methods that begin with a given prefix.
        """

        class A:
            def foo(self):
                pass

        class B(A):
            def bar(self):
                pass

        class C(B):
            def baz(self):
                pass

        d = {}
        reflect.accumulateMethods(C, d, "ba")
        self.assertEqual(d, {"bar": B.bar, "baz": C.baz})


class TestPrefixedMethodNames(unittest.SynchronousTestCase):
    """
    Tests for L{twisted.python.reflect.prefixedMethodNames}.
    """

    def test_prefixedMethodNames(self):
        """
        L{reflect.prefixedMethodNames} returns a list of method names that
        match the given prefix.
        """

        class A:
            def foo(self):
                pass

        class B(A):
            def bar(self):
                pass

        class C(B):
            def baz(self):
                pass

        self.assertEqual(reflect.prefixedMethodNames(C, "ba"), ["bar", "baz"])


class TestAccumulateClassDict(unittest.SynchronousTestCase):
    """
    Tests for L{twisted.python.reflect.accumulateClassDict}.
    """

    def test_accumulateClassDict(self):
        """
        L{reflect.accumulateClassDict} accumulates all attributes of a given
        name in a class hierarchy into a single dictionary.
        """

        class A:
            a = {"a": 1}

        class B(A):
            a = {"b": 2}

        class C(B):
            a = {"c": 3}

        d = {}
        reflect.accumulateClassDict(C, "a", d)
        self.assertEqual(d, {"a": 1, "b": 2, "c": 3})


class TestAccumulateClassList(unittest.SynchronousTestCase):
    """
    Tests for L{twisted.python.reflect.accumulateClassList}.
    """

    def test_accumulateClassList(self):
        """
        L{reflect.accumulateClassList} accumulates all attributes of a given
        name in a class hierarchy into a single list.
        """

        class A:
            a = [1]

        class B(A):
            a = [2]

        class C(B):
            a = [3]

        l = []
        reflect.accumulateClassList(C, "a", l)
        self.assertEqual(l, [1, 2, 3])


class TestFullFuncName(unittest.SynchronousTestCase):
    """
    Tests for L{twisted.python.reflect.fullFuncName}.
    """

    def test_fullFuncName(self):
        """
        L{reflect.fullFuncName} returns the fully qualified name of a function
        or method.
        """
        self.assertEqual(reflect.fullFuncName(reflect.fullFuncName), "twisted.python.reflect.fullFuncName")
        self.assertEqual(reflect.fullFuncName(reflect.Reflector), "twisted.python.reflect.Reflector")
        self.assertEqual(reflect.fullFuncName(reflect), "twisted.python.reflect")


class TestGetClass(unittest.SynchronousTestCase):
    """
    Tests for L{twisted.python.reflect.getClass}.
    """

    def test_getClass(self):
        """
        L{reflect.getClass} returns the class or type of an object.
        """
        self.assertIs(reflect.getClass(1), int)
        self.assertIs(reflect.getClass("foo"), str)
        self.assertIs(reflect.getClass(reflect), ModuleType)


class TestQual(unittest.SynchronousTestCase):
    """
    Tests for L{twisted.python.reflect.qual}.
    """

    def test_qual(self):
        """
        L{reflect.qual} returns the full import path of a class.
        """
        self.assertEqual(reflect.qual(reflect.Reflector), "twisted.python.reflect.Reflector")
        self.assertEqual(reflect.qual(reflect), "twisted.python.reflect")


class TestQueueMethod(unittest.SynchronousTestCase):
    """
    Tests for L{twisted.python.reflect.QueueMethod}.
    """

    def test_queueMethod(self):
        """
        L{reflect.QueueMethod} represents a method that doesn't exist yet.
        """
        calls: List[Tuple[str, Tuple[int]]] = []
        q = reflect.QueueMethod("foo", calls)
        q(1)
        self.assertEqual(calls, [("foo", (1,))])


class TestRegexType(unittest.SynchronousTestCase):
    """
    Tests for L{twisted.python.reflect.RegexType}.
    """

    def test_regexType(self):
        """
        L{reflect.RegexType} is the type of a compiled regular expression.
        """
        self.assertIsInstance(re.compile("foo"), reflect.RegexType)


class TestRegexType(unittest.SynchronousTestCase):
    """
    Tests for L{twisted.python.reflect.modgrep}.
    """

    def test_modgrep(self):
        """
        L{reflect.modgrep} returns a list of modules that match the given
        regular expression.
        """
        self.assertIn("twisted.python.reflect", reflect.modgrep("reflect"))


class TestFindInstances(unittest.SynchronousTestCase):
    """
    Tests for L{twisted.python.reflect.findInstances}.
    """

    def test_findInstances(self):
        """
        L{reflect.findInstances} returns a list of objects that are instances
        of the given type.
        """
        self.assertIn(self, reflect.findInstances(sys.modules, TestFindInstances))


class ReflectorTestCase(unittest.SynchronousTestCase):
    def setUp(self):
        """
        Create a reflector.
        """
        self.r = reflect.Reflector()

    def test_methods(self):
        """
        Test that the methods are called in the correct order.
        """
        calls: List[str] = []

        class Foo:
            def a(self):
                calls.append("a")

            def b(self):
                calls.append("b")

        self.r.addMethods(Foo, "a")
        self.r.addMethods(Foo, "b")
        self.r.run()
        self.assertEqual(calls, ["a", "b"])


class TestSafeRepr(unittest.SynchronousTestCase):
    """
    Tests for L{twisted.python.reflect.prefixedMethods}.
    """

    def test_prefixedMethods(self):
        """
        L{reflect.prefixedMethods} returns a list of method objects that match
        the given prefix.
        """

        class A:
            def foo(self):
                pass

        class B(A):
            def bar(self):
                pass

        class C(B):
            def baz(self):
                pass

        self.assertEqual(
            reflect.prefixedMethods(C(), "ba"),
            [B.bar, C.baz],
        )


class TestQueueMethod(unittest.SynchronousTestCase):
    """
    Tests for L{twisted.python.reflect.QueueMethod}.
    """

    def test_queueMethod(self):
        """
        L{reflect.QueueMethod} represents a method that doesn't exist yet.
        """
        calls: List[Tuple[str, Tuple[int]]] = []
        q = reflect.QueueMethod("foo", calls)
        q(1)
        self.assertEqual(calls, [("foo", (1,))])


class TestReflect(unittest.SynchronousTestCase):
    """
    Tests for L{twisted.python.reflect}.
    """

    def test_namedAny(self):
        """
        L{reflect.namedAny} returns the named object, or raises an
        exception if it doesn't exist.
        """
        self.assertIs(reflect.namedAny("twisted.python.reflect.namedAny"), reflect.namedAny)
        self.assertIs(reflect.namedAny("twisted.python.reflect.namedModule"), reflect.namedModule)
        self.assertIs(reflect.namedAny("twisted.python.reflect.namedClass"), reflect.namedClass)
        self.assertIs(reflect.namedAny("twisted.python.reflect.namedObject"), reflect.namedObject)

    def test_namedModule(self):
        """
        L{reflect.namedModule} returns the named module, or raises an
        exception if it doesn't exist.
        """
        self.assertIs(reflect.namedModule("twisted.python.reflect"), reflect)

    def test_namedClass(self):
        """
        L{reflect.namedClass} returns the named class, or raises an
        exception if it doesn't exist.
        """
        self.assertIs(reflect.namedClass("twisted.python.reflect.Reflector"), reflect.Reflector)
        self.assertIs(reflect.namedClass("twisted.python.reflect.Reflector"), reflect.Reflector)

    def test_namedObject(self):
        """
        L{reflect.namedObject} returns the named object, or raises an
        exception if it doesn't exist.
        """
        self.assertIs(reflect.namedObject("twisted.python.reflect.namedAny"), reflect.namedAny)
        self.assertIs(reflect.namedObject("twisted.python.reflect.namedModule"), reflect.namedModule)
        self.assertIs(reflect.namedObject("twisted.python.reflect.namedClass"), reflect.namedClass)
        self.assertIs(reflect.namedObject("twisted.python.reflect.namedObject"), reflect.namedObject)

    def test_namedAny_invalid(self):
        """
        L{reflect.namedAny} raises an L{InvalidName} exception if the
        named object doesn't exist.
        """
        self.assertRaises(reflect.InvalidName, reflect.namedAny, "")
        self.assertRaises(reflect.InvalidName, reflect.namedAny, "foo")
        self.assertRaises(reflect.InvalidName, reflect.namedAny, "foo.bar")
        self.assertRaises(reflect.InvalidName, reflect.namedAny, "foo.bar.baz")

    def test_namedModule_invalid(self):
        """
        L{reflect.namedModule} raises an L{InvalidName} exception if the
        named module doesn't exist.
        """
        self.assertRaises(reflect.InvalidName, reflect.namedModule, "")
        self.assertRaises(reflect.InvalidName, reflect.namedModule, "foo")
        self.assertRaises(reflect.InvalidName, reflect.namedModule, "foo.bar")

    def test_namedClass_invalid(self):
        """
        L{reflect.namedClass} raises an L{InvalidName} exception if the
        named class doesn't exist.
        """
        self.assertRaises(reflect.InvalidName, reflect.namedClass, "")
        self.assertRaises(reflect.InvalidName, reflect.namedClass, "foo")
        self.assertRaises(reflect.InvalidName, reflect.namedClass, "foo.bar")

    def test_namedObject_invalid(self):
        """
        L{reflect.namedObject} raises an L{InvalidName} exception if the
        named object doesn't exist.
        """
        self.assertRaises(reflect.InvalidName, reflect.namedObject, "")
        self.assertRaises(reflect.InvalidName, reflect.namedObject, "foo")
        self.assertRaises(reflect.InvalidName, reflect.namedObject, "foo.bar")

    def test_namedAny_module_not_found(self):
        """
        L{reflect.namedAny} raises a L{ModuleNotFound} exception if the
        named module doesn't exist.
        """
        self.assertRaises(reflect.ModuleNotFound, reflect.namedAny, "foo.bar.baz")

    def test_namedModule_module_not_found(self):
        """
        L{reflect.namedModule} raises a L{ModuleNotFound} exception if the
        named module doesn't exist.
        """
        self.assertRaises(reflect.ModuleNotFound, reflect.namedModule, "foo.bar")

    def test_namedClass_module_not_found(self):
        """
        L{reflect.namedClass} raises a L{ModuleNotFound} exception if the
        named class doesn't exist.
        """
        self.assertRaises(reflect.ModuleNotFound, reflect.namedClass, "foo.bar")

    def test_namedObject_module_not_found(self):
        """
        L{reflect.namedObject} raises a L{ModuleNotFound} exception if the
        named object doesn't exist.
        """
        self.assertRaises(reflect.ModuleNotFound, reflect.namedObject, "foo.bar")

    def test_namedAny_object_not_found(self):
        """
        L{reflect.namedAny} raises an L{ObjectNotFound} exception if the
        named object doesn't exist.
        """
        self.assertRaises(reflect.ObjectNotFound, reflect.namedAny, "twisted.python.reflect.foo")

    def test_namedModule_object_not_found(self):
        """
        L{reflect.namedModule} raises an L{ObjectNotFound} exception if the
        named module doesn't exist.
        """
        self.assertRaises(reflect.ObjectNotFound, reflect.namedModule, "twisted.python.reflect.foo")

    def test_namedClass_object_not_found(self):
        """
        L{reflect.namedClass} raises an L{ObjectNotFound} exception if the
        named class doesn't exist.
        """
        self.assertRaises(reflect.ObjectNotFound, reflect.namedClass, "twisted.python.reflect.foo")

    def test_namedObject_object_not_found(self):
        """
        L{reflect.namedObject} raises an L{ObjectNotFound} exception if the
        named object doesn't exist.
        """
        self.assertRaises(reflect.ObjectNotFound, reflect.namedObject, "twisted.python.reflect.foo")

    def test_namedAny_attribute_error(self):
        """
        L{reflect.namedAny} raises an L{AttributeError} exception if the
        named attribute doesn't exist.
        """
        self.assertRaises(AttributeError, reflect.namedAny, "twisted.python.reflect.namedAny.foo")

    def test_namedModule_attribute_error(self):
        """
        L{reflect.namedModule} raises an L{AttributeError} exception if the
        named attribute doesn't exist.
        """
        self.assertRaises(AttributeError, reflect.namedModule, "twisted.python.reflect.namedAny.foo")

    def test_namedClass_attribute_error(self):
        """
        L{reflect.namedClass} raises an L{AttributeError} exception if the
        named attribute doesn't exist.
        """
        self.assertRaises(AttributeError, reflect.namedClass, "twisted.python.reflect.namedAny.foo")

    def test_namedObject_attribute_error(self):
        """
        L{reflect.namedObject} raises an L{AttributeError} exception if the
        named attribute doesn't exist.
        """
        self.assertRaises(AttributeError, reflect.namedObject, "twisted.python.reflect.namedAny.foo")

    def test_namedAny_module(self):
        """
        L{reflect.namedAny} returns the named module.
        """
        self.assertIs(reflect.namedAny("twisted.python.reflect"), reflect)

    def test_namedModule_module(self):
        """
        L{reflect.namedModule} returns the named module.
        """
        self.assertIs(reflect.namedModule("twisted.python.reflect"), reflect)

    def test_namedClass_module(self):
        """
        L{reflect.namedClass} returns the named class.
        """
        self.assertIs(reflect.namedClass("twisted.python.reflect.Reflector"), reflect.Reflector)

    def test_namedObject_module(self):
        """
        L{reflect.namedObject} returns the named object.
        """
        self.assertIs(reflect.namedObject("twisted.python.reflect.namedAny"), reflect.namedAny)

    def test_namedAny_object(self):
        """
        L{reflect.namedAny} returns the named object.
        """
        self.assertIs(reflect.namedAny("twisted.python.reflect.namedAny"), reflect.namedAny)

    def test_namedModule_object(self):
        """
        L{reflect.namedModule} returns the named object.
        """
        self.assertIs(reflect.namedModule("twisted.python.reflect.namedAny"), reflect.namedAny)

    def test_namedClass_object(self):
        """
        L{reflect.namedClass} returns the named object.
        """
        self.assertIs(reflect.namedClass("twisted.python.reflect.namedAny"), reflect.namedAny)

    def test_namedObject_object(self):
        """
        L{reflect.namedObject} returns the named object.
        """
        self.assertIs(reflect.namedObject("twisted.python.reflect.namedAny"), reflect.namedAny)

    def test_namedAny_class(self):
        """
        L{reflect.namedAny} returns the named class.
        """
        self.assertIs(reflect.namedAny("twisted.python.reflect.Reflector"), reflect.Reflector)

    def test_namedModule_class(self):
        """
        L{reflect.namedModule} returns the named class.
        """
        self.assertIs(reflect.namedModule("twisted.python.reflect.Reflector"), reflect.Reflector)

    def test_namedClass_class(self):
        """
        L{reflect.namedClass} returns the named class.
        """
        self.assertIs(reflect.namedClass("twisted.python.reflect.Reflector"), reflect.Reflector)

    def test_namedObject_class(self):
        """
        L{reflect.namedObject} returns the named class.
        """
        self.assertIs(reflect.namedObject("twisted.python.reflect.Reflector"), reflect.Reflector)

    def test_namedAny_function(self):
        """
        L{reflect.namedAny} returns the named function.
        """
        self.assertIs(reflect.namedAny("twisted.python.reflect.namedAny"), reflect.namedAny)

    def test_namedModule_function(self):
        """
        L{reflect.namedModule} returns the named function.
        """
        self.assertIs(reflect.namedModule("twisted.python.reflect.namedAny"), reflect.namedAny)

    def test_namedClass_function(self):
        """
        L{reflect.namedClass} returns the named function.
        """
        self.assertIs(reflect.namedClass("twisted.python.reflect.namedAny"), reflect.namedAny)

    def test_namedObject_function(self):
        """
        L{reflect.namedObject} returns the named function.
        """
        self.assertIs(reflect.namedObject("twisted.python.reflect.namedAny"), reflect.namedAny)

    def test_namedAny_method(self):
        """
        L{reflect.namedAny} returns the named method.
        """
        self.assertIs(reflect.namedAny("twisted.python.reflect.Reflector.namedAny"), reflect.Reflector.namedAny)

    def test_namedModule_method(self):
        """
        L{reflect.namedModule} returns the named method.
        """
        self.assertIs(reflect.namedModule("twisted.python.reflect.Reflector.namedAny"), reflect.Reflector.namedAny)

    def test_namedClass_method(self):
        """
        L{reflect.namedClass} returns the named method.
        """
        self.assertIs(reflect.namedClass("twisted.python.reflect.Reflector.namedAny"), reflect.Reflector.namedAny)

    def test_namedObject_method(self):
        """
        L{reflect.namedObject} returns the named method.
        """
        self.assertIs(reflect.namedObject("twisted.python.reflect.Reflector.namedAny"), reflect.Reflector.namedAny)

    def test_namedAny_module_variable(self):
        """
        L{reflect.namedAny} returns the named module variable.
        """
        self.assertIs(reflect.namedAny("twisted.python.reflect.RegexType"), reflect.RegexType)

    def test_namedModule_module_variable(self):
        """
        L{reflect.namedModule} returns the named module variable.
        """
        self.assertIs(reflect.namedModule("twisted.python.reflect.RegexType"), reflect.RegexType)

    def test_namedClass_module_variable(self):
        """
        L{reflect.namedClass} returns the named module variable.
        """
        self.assertIs(reflect.namedClass("twisted.python.reflect.RegexType"), reflect.RegexType)

    def test_namedObject_module_variable(self):
        """
        L{reflect.namedObject} returns the named module variable.
        """
        self.assertIs(reflect.namedObject("twisted.python.reflect.RegexType"), reflect.RegexType)

    def test_namedAny_class_variable(self):
        """
        L{reflect.namedAny} returns the named class variable.
        """
        self.assertIs(reflect.namedAny("twisted.python.reflect.Reflector.RegexType"), reflect.RegexType)

    def test_namedModule_class_variable(self):
        """
        L{reflect.namedModule} returns the named class variable.
        """
        self.assertIs(reflect.namedModule("twisted.python.reflect.Reflector.RegexType"), reflect.RegexType)

    def test_namedClass_class_variable(self):
        """
        L{reflect.namedClass} returns the named class variable.
        """
        self.assertIs(reflect.namedClass("twisted.python.reflect.Reflector.RegexType"), reflect.RegexType)

    def test_namedObject_class_variable(self):
        """
        L{reflect.namedObject} returns the named class variable.
        """
        self.assertIs(reflect.namedObject("twisted.python.reflect.Reflector.RegexType"), reflect.RegexType)

    def test_namedAny_function_variable(self):
        """
        L{reflect.namedAny} returns the named function variable.
        """
        self.assertIs(reflect.namedAny("twisted.python.reflect.namedAny.RegexType"), reflect.RegexType)

    def test_namedModule_function_variable(self):
        """
        L{reflect.namedModule} returns the named function variable.
        """
        self.assertIs(reflect.namedModule("twisted.python.reflect.namedAny.RegexType"), reflect.RegexType)

    def test_namedClass_function_variable(self):
        """
        L{reflect.namedClass} returns the named function variable.
        """
        self.assertIs(reflect.namedClass("twisted.python.reflect.namedAny.RegexType"), reflect.RegexType)

    def test_namedObject_function_variable(self):
        """
        L{reflect.namedObject} returns the named function variable.
        """
        self.assertIs(reflect.namedObject("twisted.python.reflect.namedAny.RegexType"), reflect.RegexType)

    def test_namedAny_method_variable(self):
        """
        L{reflect.namedAny} returns the named method variable.
        """
        self.assertIs(reflect.namedAny("twisted.python.reflect.Reflector.namedAny.RegexType"), reflect.RegexType)

    def test_namedModule_method_variable(self):
        """
        L{reflect.namedModule} returns the named method variable.
        """
        self.assertIs(reflect.namedModule("twisted.python.reflect.Reflector.namedAny.RegexType"), reflect.RegexType)

    def test_namedClass_method_variable(self):
        """
        L{reflect.namedClass} returns the named method variable.
        """
        self.assertIs(reflect.namedClass("twisted.python.reflect.Reflector.namedAny.RegexType"), reflect.RegexType)

    def test_namedObject_method_variable(self):
        """
        L{reflect.namedObject} returns the named method variable.
        """
        self.assertIs(reflect.namedObject("twisted.python.reflect.Reflector.namedAny.RegexType"), reflect.RegexType)

    def test_namedAny_module_class(self):
        """
        L{reflect.namedAny} returns the named module class.
        """
        self.assertIs(reflect.namedAny("twisted.python.reflect.Reflector"), reflect.Reflector)

    def test_namedModule_module_class(self):
        """
        L{reflect.namedModule} returns the named module class.
        """
        self.assertIs(reflect.namedModule("twisted.python.reflect.Reflector"), reflect.Reflector)

    def test_namedClass_module_class(self):
        """
        L{reflect.namedClass} returns the named module class.
        """
        self.assertIs(reflect.namedClass("twisted.python.reflect.Reflector"), reflect.Reflector)

    def test_namedObject_module_class(self):
        """
        L{reflect.namedObject} returns the named module class.
        """
        self.assertIs(reflect.namedObject("twisted.python.reflect.Reflector"), reflect.Reflector)

    def test_namedAny_class_class(self):
        """
        L{reflect.namedAny} returns the named class class.
        """
        self.assertIs(reflect.namedAny("twisted.python.reflect.Reflector"), reflect.Reflector)

    def test_namedModule_class_class(self):
        """
        L{reflect.namedModule} returns the named class class.
        """
        self.assertIs(reflect.namedModule("twisted.python.reflect.Reflector"), reflect.Reflector)

    def test_namedClass_class_class(self):
        """
        L{reflect.namedClass} returns the named class class.
        """
        self.assertIs(reflect.namedClass("twisted.python.reflect.Reflector"), reflect.Reflector)

    def test_namedObject_class_class(self):
        """
        L{reflect.namedObject} returns the named class class.
        """
        self.assertIs(reflect.namedObject("twisted.python.reflect.Reflector"), reflect.Reflector)

    def test_namedAny_function_class(self):
        """
        L{reflect.namedAny} returns the named function class.
        """
        self.assertIs(reflect.namedAny("twisted.python.reflect.Reflector"), reflect.Reflector)

    def test_namedModule_function_class(self):
        """
        L{reflect.namedModule} returns the named function class.
        """
        self.assertIs(reflect.namedModule("twisted.python.reflect.Reflector"), reflect.Reflector)

    def test_namedClass_function_class(self):
        """
        L{reflect.namedClass} returns the named function class.
        """
        self.assertIs(reflect.namedClass("twisted.python.reflect.Reflector"), reflect.Reflector)

    def test_namedObject_function_class(self):
        """
        L{reflect.namedObject} returns the named function class.
        """
        self.assertIs(reflect.namedObject("twisted.python.reflect.Reflector"), reflect.Reflector)

    def test_namedAny_method_class(self):
        """
        L{reflect.namedAny} returns the named method class.
        """
        self.assertIs(reflect.namedAny("twisted.python.reflect.Reflector"), reflect.Reflector)

    def test_namedModule_method_class(self):
        """
        L{reflect.namedModule} returns the named method class.
        """
        self.assertIs(reflect.namedModule("twisted.python.reflect.Reflector"), reflect.Reflector)

    def test_namedClass_method_class(self):
        """
        L{reflect.namedClass} returns the named method class.
        """
        self.assertIs(reflect.namedClass("twisted.python.reflect.Reflector"), reflect.Reflector)

    def test_namedObject_method_class(self):
        """
        L{reflect.namedObject} returns the named method class.
        """
        self.assertIs(reflect.namedObject("twisted.python.reflect.Reflector"), reflect.Reflector)

    def test_namedAny_module_function(self):
        """
        L{reflect.namedAny} returns the named module function.
        """
        self.assertIs(reflect.namedAny("twisted.python.reflect.namedAny"), reflect.namedAny)

    def test_namedModule_module_function(self):
        """
        L{reflect.namedModule} returns the named module function.
        """
        self.assertIs(reflect.namedModule("twisted.python.reflect.namedAny"), reflect.namedAny)

    def test_namedClass_module_function(self):
        """
        L{reflect.namedClass} returns the named module function.
        """
        self.assertIs(reflect.namedClass("twisted.python.reflect.namedAny"), reflect.namedAny)

    def test_namedObject_module_function(self):
        """
        L{reflect.namedObject} returns the named module function.
        """
        self.assertIs(reflect.namedObject("twisted.python.reflect.namedAny"), reflect.namedAny)

    def test_namedAny_class_function(self):
        """
        L{reflect.namedAny} returns the named class function.
        """
        self.assertIs(reflect.namedAny("twisted.python.reflect.namedAny"), reflect.namedAny)

    def test_namedModule_class_function(self):
        """
        L{reflect.namedModule} returns the named class function.
        """
        self.assertIs(reflect.namedModule("twisted.python.reflect.namedAny"), reflect.namedAny)

    def test_namedClass_class_function(self):
        """
        L{reflect.namedClass} returns the named class function.
        """
        self.assertIs(reflect.namedClass("twisted.python.reflect.namedAny"), reflect.namedAny)

    def test_namedObject_class_function(self):
        """
        L{reflect.namedObject} returns the named class function.
        """
        self.assertIs(reflect.namedObject("twisted.python.reflect.namedAny"), reflect.namedAny)

    def test_namedAny_function_function(self):
        """
        L{reflect.namedAny} returns the named function function.
        """
        self.assertIs(reflect.namedAny("twisted.python.reflect.namedAny"), reflect.namedAny)

    def test_namedModule_function_function(self):
        """
        L{reflect.namedModule} returns the named function function.
        """
        self.assertIs(reflect.namedModule("twisted.python.reflect.namedAny"), reflect.namedAny)

    def test_namedClass_function_function(self):
        """
        L{reflect.namedClass} returns the named function function.
        """
        self.assertIs(reflect.namedClass("twisted.python.reflect.namedAny"), reflect.namedAny)

    def test_namedObject_function_function(self):
        """
        L{reflect.namedObject} returns the named function function.
        """
        self.assertIs(reflect.namedObject("twisted.python.reflect.namedAny"), reflect.namedAny)

    def test_namedAny_method_function(self):
        """
        L{reflect.namedAny} returns the named method function.
        """
        self.assertIs(reflect.namedAny("twisted.python.reflect.namedAny"), reflect.namedAny)

    def test_namedModule_method_function(self):
        """
        L{reflect.namedModule} returns the named method function.
        """
        self.assertIs(reflect.namedModule("twisted.python.reflect.namedAny"), reflect.namedAny)

    def test_namedClass_method_function(self):
        """
        L{reflect.namedClass} returns the named method function.
        """
        self.assertIs(reflect.namedClass("twisted.python.reflect.namedAny"), reflect.namedAny)

    def test_namedObject_method_function(self):
        """
        L{reflect.namedObject} returns the named method function.
        """
        self.assertIs(reflect.namedObject("twisted.python.reflect.namedAny"), reflect.namedAny)

    def test_namedAny_module_variable_function(self):
        """
        L{reflect.namedAny} returns the named module variable function.
        """
        self.assertIs(reflect.namedAny("twisted.python.reflect.RegexType"), reflect.RegexType)

    def test_namedModule_module_variable_function(self):
        """
        L{reflect.namedModule} returns the named module variable function.
        """
        self.assertIs(reflect.namedModule("twisted.python.reflect.RegexType"), reflect.RegexType)

    def test_namedClass_module_variable_function(self):
        """
        L{reflect.namedClass} returns the named module variable function.
        """
        self.assertIs(reflect.namedClass("twisted.python.reflect.RegexType"), reflect.RegexType)

    def test_namedObject_module_variable_function(self):
        """
        L{reflect.namedObject} returns the named module variable function.
        """
        self.assertIs(reflect.namedObject("twisted.python.reflect.RegexType"), reflect.RegexType)

    def test_namedAny_class_variable_function(self):
        """
        L{reflect.namedAny} returns the named class variable function.
        """
        self.assertIs(reflect.namedAny("twisted.python.reflect.RegexType"), reflect.RegexType)

    def test_namedModule_class_variable_function(self):
        """
        L{reflect.namedModule} returns the named class variable function.
        """
        self.assertIs(reflect.namedModule("twisted.python.reflect.RegexType"), reflect.RegexType)

    def test_namedClass_class_variable_function(self):
        """
        L{reflect.namedClass} returns the named class variable function.
        """
        self.assertIs(reflect.namedClass("twisted.python.reflect.RegexType"), reflect.RegexType)

    def test_namedObject_class_variable_function(self):
        """
        L{reflect.namedObject} returns the named class variable function.
        """
        self.assertIs(reflect.namedObject("twisted.python.reflect.RegexType"), reflect.RegexType)

    def test_namedAny_function_variable_function(self):
        """
        L{reflect.namedAny} returns the named function variable function.
        """
        self.assertIs(reflect.namedAny("twisted.python.reflect.RegexType"), reflect.RegexType)

    def test_namedModule_function_variable_function(self):
        """
        L{reflect.namedModule} returns the named function variable function.
        """
        self.assertIs(reflect.namedModule("twisted.python.reflect.RegexType"), reflect.RegexType)

    def test_namedClass_function_variable_function(self):
        """
        L{reflect.namedClass} returns the named function variable function.
        """
        self.assertIs(reflect.namedClass("twisted.python.reflect.RegexType"), reflect.RegexType)

    def test_namedObject_function_variable_function(self):
        """
        L{reflect.namedObject} returns the named function variable function.
        """
        self.assertIs(reflect.namedObject("twisted.python.reflect.RegexType"), reflect.RegexType)

    def test_namedAny_method_variable_function(self):
        """
        L{reflect.namedAny} returns the named method variable function.
        """
        self.assertIs(reflect.namedAny("twisted.python.reflect.RegexType"), reflect.RegexType)

    def test_namedModule_method_variable_function(self):
        """
        L{reflect.namedModule} returns the named method variable function.
        """
        self.assertIs(reflect.namedModule("twisted.python.reflect.RegexType"), reflect.RegexType)

    def test_namedClass_method_variable_function(self):
        """
        L{reflect.namedClass} returns the named method variable function.
        """
        self.assertIs(reflect.namedClass("twisted.python.reflect.RegexType"), reflect.RegexType)

    def test_namedObject_method_variable_function(self):
        """
        L{reflect.namedObject} returns the named method variable function.
        """
        self.assertIs(reflect.namedObject("twisted.python.reflect.RegexType"), reflect.RegexType)

    def test_namedAny_module_class_function(self):
        """
        L{reflect.namedAny} returns the named module class function.
        """
        self.assertIs(reflect.namedAny("twisted.python.reflect.Reflector"), reflect.Reflector)

    def test_namedModule_module_class_function(self):
        """
        L{reflect.namedModule} returns the named module class function.
        """
        self.assertIs(reflect.namedModule("twisted.python.reflect.Reflector"), reflect.Reflector)

    def test_namedClass_module_class_function(self):
        """
        L{reflect.namedClass} returns the named module class function.
        """
        self.assertIs(reflect.namedClass("twisted.python.reflect.Reflector"), reflect.Reflector)

    def test_namedObject_module_class_function(self):
        """
        L{reflect.namedObject} returns the named module class function.
        """
        self.assertIs(reflect.namedObject("twisted.python.reflect.Reflector"), reflect.Reflector)

    def test_namedAny_class_class_function(self):
        """
        L{reflect.namedAny} returns the named class class function.
        """
        self.assertIs(reflect.namedAny("twisted.python.reflect.Reflector"), reflect.Reflector)

    def test_namedModule_class_class_function(self):
        """
        L{reflect.namedModule} returns the named class class function.
        """
        self.assertIs(reflect.namedModule("twisted.python.reflect.Reflector"), reflect.Reflector)

    def test_namedClass_class_class_function(self):
        """
        L{reflect.namedClass} returns the named class class function.
        """
        self.assertIs(reflect.namedClass("twisted.python.reflect.Reflector"), reflect.Reflector)

    def test_namedObject_class_class_function(self):
        """
        L{reflect.namedObject} returns the named class class function.
        """
        self.assertIs(reflect.namedObject("twisted.python.reflect.Reflector"), reflect.Reflector)

    def test_namedAny_function_class_function(self):
        """
        L{reflect.namedAny} returns the named function class function.
        """
        self.assertIs(reflect.namedAny("twisted.python.reflect.Reflector"), reflect.Reflector)

    def test_namedModule_function_class_function(self):
        """
        L{reflect.namedModule} returns the named function class function.
        """
        self.assertIs(reflect.namedModule("twisted.python.reflect.Reflector"), reflect.Reflector)

    def test_namedClass_function_class_function(self):
        """
        L{reflect.namedClass} returns the named function class function.
        """
        self.assertIs(reflect.namedClass("twisted.python.reflect.Reflector"), reflect.Reflector)

    def test_namedObject_function_class_function(self):
        """
        L{reflect.namedObject} returns the named function class function.
        """
        self.assertIs(reflect.namedObject("twisted.python.reflect.Reflector"), reflect.Reflector)

    def test_namedAny_method_class_function(self):
        """
        L{reflect.namedAny} returns the named method class function.
        """
        self.assertIs(reflect.namedAny("twisted.python.reflect.Reflector"), reflect.Reflector)

    def test_namedModule_method_class_function(self):
        """
        L{reflect.namedModule} returns the named method class function.
        """
        self.assertIs(reflect.namedModule("twisted.python.reflect.Reflector"), reflect.Reflector)

    def test_namedClass_method_class_function(self):
        """
        L{reflect.namedClass} returns the named method class function.
        """
        self.assertIs(reflect.namedClass("twisted.python.reflect.Reflector"), reflect.Reflector)

    def test_namedObject_method_class_function(self):
        """
        L{reflect.namedObject} returns the named method class function.
        """
        self.assertIs(reflect.namedObject("twisted.python.reflect.Reflector"), reflect.Reflector)

    def test_namedAny_module_function_function(self):
        """
        L{reflect.namedAny} returns the named module function function.
        """
        self.assertIs(reflect.namedAny("twisted.python.reflect.namedAny"), reflect.namedAny)

    def test_namedModule_module_function_function(self):
        """
        L{reflect.namedModule} returns the named module function function.
        """
        self.assertIs(reflect.namedModule("twisted.python.reflect.namedAny"), reflect.namedAny)

    def test_namedClass_module_function_function(self):
        """
        L{reflect.namedClass} returns the named module function function.
        """
        self.assertIs(reflect.namedClass("twisted.python.reflect.namedAny"), reflect.namedAny)

    def test_namedObject_module_function_function(self):
        """
        L{reflect.namedObject} returns the named module function function.
        """
        self.assertIs(reflect.namedObject("twisted.python.reflect.namedAny"), reflect.namedAny)

    def test_namedAny_class_function_function(self):
        """
        L{reflect.namedAny} returns the named class function function.
        """
        self.assertIs(reflect.namedAny("twisted.python.reflect.namedAny"), reflect.namedAny)

    def test_namedModule_class_function_function(self):
        """
        L{reflect.namedModule} returns the named class function function.
        """
        self.assertIs(reflect.namedModule("twisted.python.reflect.namedAny"), reflect.namedAny)

    def test_namedClass_class_function_function(self):
        """
        L{reflect.namedClass} returns the named class function function.
        """
        self.assertIs(reflect.namedClass("twisted.python.reflect.namedAny"), reflect.namedAny)

    def test_namedObject_class_function_function(self):
        """
        L{reflect.namedObject} returns the named class function function.
        """
        self.assertIs(reflect.namedObject("twisted.python.reflect.namedAny"), reflect.namedAny)

    def test_namedAny_function_function_function(self):
        """
        L{reflect.namedAny} returns the named function function function.
        """
        self.assertIs(reflect.namedAny("twisted.python.reflect.namedAny"), reflect.namedAny)

    def test_namedModule_function_function_function(self):
        """
        L{reflect.namedModule} returns the named function function function.
        """
        self.assertIs(reflect.namedModule("twisted.python.reflect.namedAny"), reflect.namedAny)

    def test_namedClass_function_function_function(self):
        """
        L{reflect.namedClass} returns the named function function function.
        """
        self.assertIs(reflect.namedClass("twisted.python.reflect.namedAny"), reflect.namedAny)

    def test_namedObject_function_function_function(self):
        """
        L{reflect.namedObject} returns the named function function function.
        """
        self.assertIs(reflect.namedObject("twisted.python.reflect.namedAny"), reflect.namedAny)

    def test_namedAny_method_function_function(self):
        """
        L{reflect.namedAny} returns the named method function function.
        """
        self.assertIs(reflect.namedAny("twisted.python.reflect.namedAny"), reflect.namedAny)

    def test_namedModule_method_function_function(self):
        """
        L{reflect.namedModule} returns the named method function function.
        """
        self.assertIs(reflect.namedModule("twisted.python.reflect.namedAny"), reflect.namedAny)

    def test_namedClass_method_function_function(self):
        """
        L{reflect.namedClass} returns the named method function function.
        """
        self.assertIs(reflect.namedClass("twisted.python.reflect.namedAny"), reflect.namedAny)

    def test_namedObject_method_function_function(self):
        """
        L{reflect.namedObject} returns the named method function function.
        """
        self.assertIs(reflect.namedObject("twisted.python.reflect.namedAny"), reflect.namedAny)

    def test_namedAny_module_variable_function_function(self):
        """
        L{reflect.namedAny} returns the named module variable function function.
        """
        self.assertIs(reflect.namedAny("twisted.python.reflect.RegexType"), reflect.RegexType)

    def test_namedModule_module_variable_function_function(self):
        """
        L{reflect.namedModule} returns the named module variable function function.
        """
        self.assertIs(reflect.namedModule("twisted.python.reflect.RegexType"), reflect.RegexType)

    def test_namedClass_module_variable_function_function(self):
        """
        L{reflect.namedClass} returns the named module variable function function.
        """
        self.assertIs(reflect.namedClass("twisted.python.reflect.RegexType"), reflect.RegexType)

    def test_namedObject_module_variable_function_function(self):
        """
        L{reflect.namedObject} returns the named module variable function function.
        """
        self.assertIs(reflect.namedObject("twisted.python.reflect.RegexType"), reflect.RegexType)

    def test_namedAny_class_variable_function_function(self):
        """
        L{reflect.namedAny} returns the named class variable function function.
        """
        self.assertIs(reflect.namedAny("twisted.python.reflect.RegexType"), reflect.RegexType)

    def test_namedModule_class_variable_function_function(self):
        """
        L{reflect.namedModule} returns the named class variable function function.
        """
        self.assertIs(reflect.namedModule("twisted.python.reflect.RegexType"), reflect.RegexType)

    def test_namedClass_class_variable_function_function(self):
        """
        L{reflect.namedClass} returns the named class variable function function.
        """
        self.assertIs(reflect.namedClass("twisted.python.reflect.RegexType"), reflect.RegexType)

    def test_namedObject_class_variable_function_function(self):
        """
        L{reflect.namedObject} returns the named class variable function function.
        """
        self.assertIs(reflect.namedObject("twisted.python.reflect.RegexType"), reflect.RegexType)

    def test_namedAny_function_variable_function_function(self):
        """
        L{reflect.namedAny} returns the named function variable function function.
        """
        self.assertIs(reflect.namedAny("twisted.python.reflect.RegexType"), reflect.RegexType)

    def test_namedModule_function_variable_function_function(self):
        """
        L{reflect.namedModule} returns the named function variable function function.
        """
        self.assertIs(reflect.namedModule("twisted.python.reflect.RegexType"), reflect.RegexType)

    def test_namedClass_function_variable_function_function(self):
        """
        L{reflect.namedClass} returns the named function variable function function.
        """
        self.assertIs(reflect.namedClass("twisted.python.reflect.RegexType"), reflect.RegexType)

    def test_namedObject_function_variable_function_function(self):
        """
        L{reflect.namedObject} returns the named function variable function function.
        """
        self.assertIs(reflect.namedObject("twisted.python.reflect.RegexType"), reflect.RegexType)

    def test_namedAny_method_variable_function_function(self):
        """
        L{reflect.namedAny} returns the named method variable function function.
        """
        self.assertIs(reflect.namedAny("twisted.python.reflect.RegexType"), reflect.RegexType)

    def test_namedModule_method_variable_function_function(self):
        """
        L{reflect.namedModule} returns the named method variable function function.
        """
        self.assertIs(reflect.namedModule("twisted.python.reflect.RegexType"), reflect.RegexType)

    def test_namedClass_method_variable_function_function(self):
        """
        L{reflect.namedClass} returns the named method variable function function.
        """
        self.assertIs(reflect.namedClass("twisted.python.reflect.RegexType"), reflect.RegexType)

    def test_namedObject_method_variable_function_function(self):
        """
        L{reflect.namedObject} returns the named method variable function function.
        """
        self.assertIs(reflect.namedObject("twisted.python.reflect.RegexType"), reflect.RegexType)

    def test_namedAny_module_class_function_function(self):
        """
        L{reflect.namedAny} returns the named module class function function.
        """
        self.assertIs(reflect.namedAny("twisted.python.reflect.Reflector"), reflect.Reflector)

    def test_namedModule_module_class_function_function(self):
        """
        L{reflect.namedModule} returns the named module class function function.
        """
        self.assertIs(reflect.namedModule("twisted.python.reflect.Reflector"), reflect.Reflector)

    def test_namedClass_module_class_function_function(self):
        """
        L{reflect.namedClass} returns the named module class function function.
        """
        self.assertIs(reflect.namedClass("twisted.python.reflect.Reflector"), reflect.Reflector)

    def test_namedObject_module_class_function_function(self):
        """
        L{reflect.namedObject} returns the named module class function function.
        """
        self.assertIs(reflect.namedObject("twisted.python.reflect.Reflector"), reflect.Reflector)

    def test_namedAny_class_class_function_function(self):
        """
        L{reflect.namedAny} returns the named class class function function.
        """
        self.assertIs(reflect.namedAny("twisted.python.reflect.Reflector"), reflect.Reflector)

    def test_namedModule_class_class_function_function(self):
        """
        L{reflect.namedModule} returns the named class class function function.
        """
        self.assertIs(reflect.namedModule("twisted.python.reflect.Reflector"), reflect.Reflector)

    def test_namedClass_class_class_function_function(self):
        """
        L{reflect.namedClass} returns the named class class function function.
        """
        self.assertIs(reflect.namedClass("twisted.python.reflect.Reflector"), reflect.Reflector)

    def test_namedObject_class_class_function_function(self):
        """
        L{reflect.namedObject} returns the named class class function function.
        """
        self.assertIs(reflect.namedObject("twisted.python.reflect.Reflector"), reflect.Reflector)

    def test_namedAny_function_class_function_function(self):
        """
        L{reflect.namedAny} returns the named function class function function.
        """
        self.assertIs(reflect.namedAny("twisted.python.reflect.Reflector"), reflect.Reflector)

    def test_namedModule_function_class_function_function(self):
        """
        L{reflect.namedModule} returns the named function class function function.
        """
        self.assertIs(reflect.namedModule("twisted.python.reflect.Reflector"), reflect.Reflector)

    def test_namedClass_function_class_function_function(self):
        """
        L{reflect.namedClass} returns the named function class function function.
        """
        self.assertIs(reflect.namedClass("twisted.python.reflect.Reflector"), reflect.Reflector)

    def test_namedObject_function_class_function_function(self):
        """
        L{reflect.namedObject} returns the named function class function function.
        """
        self.assertIs(reflect.namedObject("twisted.python.reflect.Reflector"), reflect.Reflector)

    def test_namedAny_method_class_function_function(self):
        """
        L{reflect.namedAny} returns the named method class function function.
        """
        self.assertIs(reflect.namedAny("twisted.python.reflect.Reflector"), reflect.Reflector)

    def test_namedModule_method_class_function_function(self):
        """
        L{reflect.namedModule} returns the named method class function function.
        """
        self.assertIs(reflect.namedModule("twisted.python.reflect.Reflector"), reflect.Reflector)

    def test_namedClass_method_class_function_function(self):
        """
        L{reflect.namedClass} returns the named method class function function.
        """
        self.assertIs(reflect.namedClass("twisted.python.reflect.Reflector"), reflect.Reflector)

    def test_namedObject_method_class_function_function(self):
        """
        L{reflect.namedObject} returns the named method class function function.
        """
        self.assertIs(reflect.namedObject("twisted.python.reflect.Reflector"), reflect.Reflector)

    def test_namedAny_module_function_function_function(self):
        """
        L{reflect.namedAny} returns the named module function function function.
        """
        self.assertIs(reflect.namedAny("twisted.python.reflect.namedAny"), reflect.namedAny)

    def test_namedModule_module_function_function_function(self):
        """
        L{reflect.namedModule} returns the named module function function function.
        """
        self.assertIs(reflect.namedModule("twisted.python.reflect.namedAny"), reflect.namedAny)

    def test_namedClass_module_function_function_function(self):
        """
        L{reflect.namedClass} returns the named module function function function.
        """
        self.assertIs(reflect.namedClass("twisted.python.reflect.namedAny"), reflect.namedAny)

    def test_namedObject_module_function_function_function(self):
        """
        L{reflect.namedObject} returns the named module function function function.
        """
        self.assertIs(reflect.namedObject("twisted.python.reflect.namedAny"), reflect.namedAny)

    def test_namedAny_class_function_function_function(self):
        """
        L{reflect.namedAny} returns the named class function function function.
        """
        self.assertIs(reflect.namedAny("twisted.python.reflect.namedAny"), reflect.namedAny)

    def test_namedModule_class_function_function_function(self):
        """
        L{reflect.namedModule} returns the named class function function function.
        """
        self.assertIs(reflect.namedModule("twisted.python.reflect.namedAny"), reflect.namedAny)

    def test_namedClass_class_function_function_function(self):
        """
        L{reflect.namedClass} returns the named class function function function.
        """
        self.assertIs(reflect.namedClass("twisted.python.reflect.namedAny"), reflect.namedAny)

    def test_namedObject_class_function_function_function(self):
        """
        L{reflect.namedObject} returns the named class function function function.
        """
        self.assertIs(reflect.namedObject("twisted.python.reflect.namedAny"), reflect.namedAny)

    def test_namedAny_function_function_function_function(self):
        """
        L{reflect.namedAny} returns the named function function function function.
        """
        self.assertIs(reflect.namedAny("twisted.python.reflect.namedAny"), reflect.namedAny)

    def test_namedModule_function_function_function_function(self):
        """
        L{reflect.namedModule} returns the named function function function function.
        """
        self.assertIs(reflect.namedModule("twisted.python.reflect.namedAny"), reflect.namedAny)

    def test_namedClass_function_function_function_function(self):
        """
        L{reflect.namedClass} returns the named function function function function.
        """
        self.assertIs(reflect.namedClass("twisted.python.reflect.namedAny"), reflect.namedAny)

    def test_namedObject_function_function_function_function(self):
        """
        L{reflect.namedObject} returns the named function function function function.
        """
        self.assertIs(reflect.namedObject("twisted.python.reflect.namedAny"), reflect.namedAny)

    def test_namedAny_method_function_function_function(self):
        """
        L{reflect.namedAny} returns the named method function function function.
        """
        self.assertIs(reflect.namedAny("twisted.python.reflect.namedAny"), reflect.namedAny)

    def test_namedModule_method_function_function_function(self):
        """
        L{reflect.namedModule} returns the named method function function function.
        """
        self.assertIs(reflect.namedModule("twisted.python.reflect.namedAny"), reflect.namedAny)

    def test_namedClass_method_function_function_function(self):
        """
        L{reflect.namedClass} returns the named method function function function.
        """
        self.assertIs(reflect.namedClass("twisted.python.reflect.namedAny"), reflect.namedAny)

    def test_namedObject_method_function_function_function(self):
        """
        L{reflect.namedObject} returns the named method function function function.
        """
        self.assertIs(reflect.namedObject("twisted.python.reflect.namedAny"), reflect.namedAny)


class TestNamedAny(unittest.SynchronousTestCase):
    """
    Tests for L{twisted.python.reflect.namedAny}
    """

    def test_basicTypes(self):
        """
        Test that the basic types can be retrieved.
        """
        self.assertIs(namedAny("twisted.python.reflect.sys"), sys)
        self.assertIs(namedAny("twisted.python.reflect.sys.version"), sys.version)
        self.assertIs(namedAny("twisted.python.reflect.QueueMethod"), reflect.QueueMethod)

    def test_attributes(self):
        """
        Test that attributes of classes can be retrieved.
        """
        self.assertIs(namedAny("twisted.python.reflect.QueueMethod.__init__"), reflect.QueueMethod.__init__)

    def test_module_class(self):
        """
        Test that a class in a module can be retrieved.
        """
        self.assertIs(namedAny("twisted.python.test.test_reflect.TestNamedAny"), TestNamedAny)

    def test_module_function(self):
        """
        Test that a function in a module can be retrieved.
        """
        self.assertIs(namedAny("twisted.python.reflect.namedAny"), namedAny)

    def test_module_class_method(self):
        """
        Test that a method of a class in a module can be retrieved.
        """
        self.assertIs(namedAny("twisted.python.test.test_reflect.TestNamedAny.test_module_class_method"), self.test_module_class_method)

    def test_module_variable(self):
        """
        Test that a variable in a module can be retrieved.
        """
        self.assertIs(namedAny("twisted.python.reflect.RegexType"), reflect.RegexType)

    def test_invalid_name(self):
        """
        L{namedAny} raises L{InvalidName} when it is given an invalid name.
        """
        self.assertRaises(reflect.InvalidName, namedAny, "")
        self.assertRaises(reflect.InvalidName, namedAny, ".")
        self.assertRaises(reflect.InvalidName, namedAny, "sys.version.")
        self.assertRaises(reflect.InvalidName, namedAny, "sys..version")
        self.assertRaises(reflect.InvalidName, namedAny, "invalid_module_name")

    def test_module_not_found(self):
        """
        L{namedAny} raises L{ModuleNotFound} when the specified module cannot
        be found.
        """
        self.assertRaises(reflect.ModuleNotFound, namedAny, "invalid_module_name.version")

    def test_object_not_found(self):
        """
        L{namedAny} raises L{ObjectNotFound} when the specified object cannot
        be found.
        """
        self.assertRaises(reflect.ObjectNotFound, namedAny, "sys.invalid_attribute_name")

    def test_attribute_error(self):
        """
        L{namedAny} raises L{AttributeError} when the specified object cannot be
        found.
        """
        self.assertRaises(AttributeError, namedAny, "twisted.python.reflect.QueueMethod.invalid_attribute_name")


class TestFilenameToModuleName(unittest.SynchronousTestCase):
    """
    Tests for L{twisted.python.reflect.filenameToModuleName}.
    """

    def test_filenameToModuleName(self):
        """
        L{reflect.filenameToModuleName} returns the dotted name of a module
        that would be imported if that filename were imported.
        """
        self.assertEqual(
            reflect.filenameToModuleName(os.path.abspath("twisted")),
            "twisted",
        )
        self.assertEqual(
            reflect.filenameToModuleName("twisted"),
            "twisted",
        )
        self.assertEqual(
            reflect.filenameToModuleName("twisted/__init__.py"),
            "twisted",
        )
        self.assertEqual(
            reflect.filenameToModuleName("twisted/test/test_reflect.py"),
            "twisted.test.test_reflect",
        )
        self.assertEqual(
            reflect.filenameToModuleName("twisted/test/test_reflect"),
            "twisted.test.test_reflect",
        )

    def test_filenameToModuleName_unicode(self):
        """
        L{reflect.filenameToModuleName} accepts both C{bytes} and C{unicode}
        filenames on Python 3.
        """
        self.assertEqual(
            reflect.filenameToModuleName(b"twisted/test/test_reflect.py"),
            "twisted.test.test_reflect",
        )
        self.assertEqual(
            reflect.filenameToModuleName(u"twisted/test/test_reflect.py"),
            "twisted.test.test_reflect",
        )


class TestNamedModule(unittest.SynchronousTestCase):
    """
    Tests for L{twisted.python.reflect.namedModule}.
    """

    def test_namedModule(self):
        """
        L{reflect.namedModule} imports and returns the module with the given
        name.
        """
        self.assertIs(namedModule("twisted.python"), import_module("twisted.python"))
        self.assertIs(namedModule("twisted.python.reflect"), import_module("twisted.python.reflect"))


class TestFullyQualifiedName(unittest.SynchronousTestCase):
    """
    Tests for L{twisted.python.reflect.fullyQualifiedName}.
    """

    def test_fullyQualifiedName(self):
        """
        L{reflect.fullyQualifiedName} returns the fully qualified name of a
        module, class, method or function.
        """
        self.assertEqual(reflect.fullyQualifiedName(reflect.fullyQualifiedName), "twisted.python.reflect.fullyQualifiedName")
        self.assertEqual(reflect.fullyQualifiedName(reflect.Reflector), "twisted.python.reflect.Reflector")
        self.assertEqual(reflect.fullyQualifiedName(reflect), "twisted.python.reflect")
        self.assertEqual(reflect.fullyQualifiedName(reflect.fullyQualifiedName.__call__), "twisted.python.reflect.fullyQualifiedName.__call__")


class TestSafeRepr(unittest.SynchronousTestCase):
    """
    Tests for L{twisted.python.reflect.safe_repr}.
    """

    def test_safe_repr(self):
        """
        L{reflect.safe_repr} returns a string representation of an object, or a
        string containing a traceback, if that object's C{__repr__} raised an
        exception.
        """

        class BrokenRepr:
            def __repr__(self):
                1 / 0

        self.assertEqual(
            reflect.safe_repr(BrokenRepr()),
            "<BrokenRepr instance at 0x{:x} with repr error:\n Traceback (most recent call last):\n ZeroDivisionError: division by zero\n>".format(
                id(BrokenRepr())
            ),
        )
        self.assertEqual(
            reflect.safe_repr("foo"),
            repr("foo"),
        )


class TestSafeStr(unittest.SynchronousTestCase):
    """
    Tests for L{twisted.python.reflect.safe_str}.
    """

    def test_safe_str(self):
        """
        L{reflect.safe_str} returns a string representation of an object, or a
        string containing a traceback, if that object's C{__str__} raised an
        exception.
        """

        class BrokenStr:
            def __str__(self):
                1 / 0

        self.assertEqual(
            reflect.safe_str(BrokenStr()),
            "<BrokenStr instance at 0x{:x} with str error:\n Traceback (most recent call last):\n ZeroDivisionError: division by zero\n>".format(
                id(BrokenStr())
            ),
        )
        self.assertEqual(
            reflect.safe_str("foo"),
            str("foo"),
        )


class TestAddMethodNamesToDict(unittest.SynchronousTestCase):
    """
    Tests for L{twisted.python.reflect.addMethodNamesToDict}.
    """

    def test_addMethodNamesToDict(self):
        """
        L{reflect.addMethodNamesToDict} goes through a class and its bases and
        puts method names starting with a given prefix in a given dictionary.
        """

        class A:
            def foo(self):
                pass

        class B(A):
            def bar(self):
                pass

        class C(B):
            def baz(self):
                pass

        d = {}
        reflect.addMethodNamesToDict(C, d, "ba")
        self.assertEqual(d, {"bar": 1, "baz": 1})


class TestAccumulateMethods(unittest.SynchronousTestCase):
    """
    Tests for L{twisted.python.reflect.accumulateMethods}.
    """

    def test_accumulateMethods(self):
        """
        L{reflect.accumulateMethods} goes through a class and its bases and
        adds all methods that begin with a given prefix.
        """

        class A:
            def foo(self):
                pass

        class B(A):
            def bar(self):
                pass

        class C(B):
            def baz(self):
                pass

        d = {}
        reflect.accumulateMethods(C, d, "ba")
        self.assertEqual(d, {"bar": B.bar, "baz": C.baz})


class TestPrefixedMethodNames(unittest.SynchronousTestCase):
    """
    Tests for L{twisted.python.reflect.prefixedMethodNames}.
    """

    def test_prefixedMethodNames(self):
        """
        L{reflect.prefixedMethodNames} returns a list of method names that
        match the given prefix.
        """

        class A:
            def foo(self):
                pass

        class B(A):
            def bar(self):
                pass

        class C(B):
            def baz(self):
                pass

        self.assertEqual(reflect.prefixedMethodNames(C, "ba"), ["bar", "baz"])


class TestAccumulateClassDict(unittest.SynchronousTestCase):
    """
    Tests for L{twisted.python.reflect.accumulateClassDict}.
    """

    def test_accumulateClassDict(self