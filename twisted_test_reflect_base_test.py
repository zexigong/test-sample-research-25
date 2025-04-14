# -*- test-case-name: twisted.test.test_reflect -*-
# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

"""
Tests for twisted.python.reflect module.
"""

from twisted.trial import unittest
from twisted.python.reflect import (
    prefixedMethodNames,
    addMethodNamesToDict,
    prefixedMethods,
    accumulateMethods,
    namedModule,
    namedObject,
    namedAny,
    filenameToModuleName,
    requireModule,
    InvalidName,
    ModuleNotFound,
    ObjectNotFound,
    safe_repr,
    safe_str,
    fullFuncName,
    getClass,
    accumulateClassDict,
    accumulateClassList,
    isSame,
    isLike,
    modgrep,
    isOfType,
    findInstances,
)


class ReflectTests(unittest.TestCase):
    def test_prefixedMethodNames(self):
        class SampleClass:
            def prefix_method1(self):
                pass

            def prefix_method2(self):
                pass

            def other_method(self):
                pass

        result = prefixedMethodNames(SampleClass, "prefix_")
        self.assertIn("method1", result)
        self.assertIn("method2", result)
        self.assertNotIn("other_method", result)

    def test_addMethodNamesToDict(self):
        class SampleClass:
            def prefix_method1(self):
                pass

            def prefix_method2(self):
                pass

            def other_method(self):
                pass

        methodsDict = {}
        addMethodNamesToDict(SampleClass, methodsDict, "prefix_")
        self.assertIn("method1", methodsDict)
        self.assertIn("method2", methodsDict)
        self.assertNotIn("other_method", methodsDict)

    def test_prefixedMethods(self):
        class SampleClass:
            def prefix_method1(self):
                pass

            def prefix_method2(self):
                pass

            def other_method(self):
                pass

        instance = SampleClass()
        result = prefixedMethods(instance, "prefix_")
        self.assertEqual(len(result), 2)
        self.assertTrue(callable(result[0]))
        self.assertTrue(callable(result[1]))

    def test_accumulateMethods(self):
        class SampleClass:
            def prefix_method1(self):
                pass

            def prefix_method2(self):
                pass

            def other_method(self):
                pass

        instance = SampleClass()
        methodsDict = {}
        accumulateMethods(instance, methodsDict, "prefix_")
        self.assertEqual(len(methodsDict), 2)
        self.assertTrue(callable(methodsDict["method1"]))
        self.assertTrue(callable(methodsDict["method2"]))

    def test_namedModule(self):
        module = namedModule("twisted.python.reflect")
        self.assertEqual(module.__name__, "twisted.python.reflect")

    def test_namedObject(self):
        obj = namedObject("twisted.python.reflect.namedObject")
        self.assertEqual(obj, namedObject)

    def test_namedAny_invalidName(self):
        with self.assertRaises(InvalidName):
            namedAny("")

        with self.assertRaises(InvalidName):
            namedAny(".")

        with self.assertRaises(InvalidName):
            namedAny("invalid..name")

    def test_namedAny_moduleNotFound(self):
        with self.assertRaises(ModuleNotFound):
            namedAny("non.existent.module")

    def test_namedAny_objectNotFound(self):
        with self.assertRaises(ObjectNotFound):
            namedAny("twisted.python.reflect.nonexistent")

    def test_namedAny_valid(self):
        obj = namedAny("twisted.python.reflect.namedAny")
        self.assertEqual(obj, namedAny)

    def test_filenameToModuleName(self):
        moduleName = filenameToModuleName("twisted/python/reflect.py")
        self.assertEqual(moduleName, "twisted.python.reflect")

    def test_requireModule(self):
        module = requireModule("twisted.python.reflect")
        self.assertEqual(module.__name__, "twisted.python.reflect")

        default = object()
        result = requireModule("non.existent.module", default)
        self.assertIs(result, default)

    def test_safe_repr(self):
        class ReprRaises:
            def __repr__(self):
                raise Exception("repr failed")

        obj = ReprRaises()
        result = safe_repr(obj)
        self.assertIn("<ReprRaises instance at 0x", result)
        self.assertIn("with repr error:", result)

    def test_safe_str(self):
        class StrRaises:
            def __str__(self):
                raise Exception("str failed")

        obj = StrRaises()
        result = safe_str(obj)
        self.assertIn("<StrRaises instance at 0x", result)
        self.assertIn("with str error:", result)

    def test_safe_str_bytes(self):
        obj = b"\xff"
        result = safe_str(obj)
        self.assertEqual(result, "<bytes instance at 0x")

    def test_fullFuncName(self):
        def sampleFunction():
            pass

        name = fullFuncName(sampleFunction)
        self.assertEqual(name, "twisted.test_reflect.test_reflect.sampleFunction")

    def test_getClass(self):
        class SampleClass:
            pass

        instance = SampleClass()
        self.assertEqual(getClass(instance), SampleClass)

    def test_accumulateClassDict(self):
        class BaseClass:
            attr = {"key1": "value1"}

        class DerivedClass(BaseClass):
            attr = {"key2": "value2"}

        resultDict = {}
        accumulateClassDict(DerivedClass, "attr", resultDict)
        self.assertEqual(resultDict, {"key1": "value1", "key2": "value2"})

    def test_accumulateClassList(self):
        class BaseClass:
            attr = ["value1"]

        class DerivedClass(BaseClass):
            attr = ["value2"]

        resultList = []
        accumulateClassList(DerivedClass, "attr", resultList)
        self.assertEqual(resultList, ["value1", "value2"])

    def test_isSame(self):
        obj = object()
        self.assertTrue(isSame(obj, obj))
        self.assertFalse(isSame(obj, object()))

    def test_isLike(self):
        self.assertTrue(isLike("test", "test"))
        self.assertFalse(isLike("test", "different"))

    def test_modgrep(self):
        paths = modgrep("twisted")
        self.assertTrue(any(path.startswith("sys.modules") for path in paths))

    def test_isOfType(self):
        self.assertTrue(isOfType("test", str))
        self.assertFalse(isOfType("test", int))

    def test_findInstances(self):
        instances = findInstances(sys.modules, dict)
        self.assertTrue(any(instance.startswith("sys.modules") for instance in instances))