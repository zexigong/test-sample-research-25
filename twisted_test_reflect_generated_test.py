from __future__ import annotations

import builtins
import collections
import importlib
import inspect
import itertools
import os
import pickle
import re
import sys
import types
import weakref
from collections import deque
from io import BytesIO, StringIO
from typing import Any, Callable, Generator, List, Tuple, TypeVar, Union
from unittest import mock

import pytest

from twisted.python import reflect

T = TypeVar("T")


class TestPrefixedMethodNames:
    def test_prefix(self) -> None:
        """
        prefixedMethodNames only returns methods that start with the given prefix.
        """

        class C:
            def prefix_b(self) -> None:
                pass

            def prefix_a(self) -> None:
                pass

            def suffix_a(self) -> None:
                pass

        results = reflect.prefixedMethodNames(C, "prefix_")
        assert sorted(results) == ["a", "b"]

    def test_inherited(self) -> None:
        """
        prefixedMethodNames returns methods that are inherited from base classes.
        """

        class Base:
            def prefix_b(self) -> None:
                pass

        class Derived(Base):
            def prefix_a(self) -> None:
                pass

        results = reflect.prefixedMethodNames(Derived, "prefix_")
        assert sorted(results) == ["a", "b"]

    def test_overridden(self) -> None:
        """
        prefixedMethodNames returns the name of overridden methods only once.
        """

        class Base:
            def prefix_a(self) -> None:
                pass

        class Derived(Base):
            def prefix_a(self) -> None:
                pass

        results = reflect.prefixedMethodNames(Derived, "prefix_")
        assert results == ["a"]


class TestNamedModule:
    def test_module(self) -> None:
        """
        namedModule loads a module by its fully-qualified name and returns it.
        """
        sys.modules.pop("os", None)
        reflect.namedModule("os")
        assert "os" in sys.modules

    def test_submodule(self) -> None:
        """
        namedModule loads a submodule by its fully-qualified name and returns it.
        """
        sys.modules.pop("twisted.python.reflect", None)
        reflect.namedModule("twisted.python.reflect")
        assert "twisted.python.reflect" in sys.modules

    def test_notFound(self) -> None:
        """
        If the module is not found, namedModule raises ImportError.
        """
        with pytest.raises(ImportError):
            reflect.namedModule("twisted.moduleThatDoesNotExist")


class TestNamedObject:
    def test_object(self) -> None:
        """
        namedObject returns a reference to the named object.
        """
        assert reflect.namedObject("twisted.python.reflect.namedObject") is reflect.namedObject

    def test_class(self) -> None:
        """
        namedObject returns a reference to the named class.
        """
        assert reflect.namedObject("twisted.python.reflect.QueueMethod") is reflect.QueueMethod

    def test_module(self) -> None:
        """
        namedObject returns a reference to the named module.
        """
        assert reflect.namedObject("twisted.python.reflect") is reflect

    def test_notFound(self) -> None:
        """
        If the object is not found, namedObject raises AttributeError.
        """
        with pytest.raises(AttributeError):
            reflect.namedObject("twisted.python.reflect.NoSuchObject")


class TestRequireModule:
    def test_found(self) -> None:
        """
        If the module is found, requireModule returns the module.
        """
        module = reflect.requireModule("twisted.python.reflect", None)
        assert module is reflect

    def test_notFound(self) -> None:
        """
        If the module is not found, requireModule returns the default argument.
        """
        assert reflect.requireModule("twisted.moduleThatDoesNotExist", None) is None

    def test_missingImport(self) -> None:
        """
        If the module is not found due to a missing import, requireModule raises ImportError.
        """
        with mock.patch("builtins.__import__", side_effect=ImportError):
            with pytest.raises(ImportError):
                reflect.requireModule("twisted.moduleThatDoesNotExist", None)


class TestNamedAny:
    def test_empty(self) -> None:
        """
        If the name is an empty string, namedAny raises InvalidName.
        """
        with pytest.raises(reflect.InvalidName):
            reflect.namedAny("")

    def test_startsWithDot(self) -> None:
        """
        If the name starts with a dot, namedAny raises InvalidName.
        """
        with pytest.raises(reflect.InvalidName):
            reflect.namedAny(".twisted")

    def test_endsWithDot(self) -> None:
        """
        If the name ends with a dot, namedAny raises InvalidName.
        """
        with pytest.raises(reflect.InvalidName):
            reflect.namedAny("twisted.")

    def test_twoDots(self) -> None:
        """
        If the name contains two dots in a row, namedAny raises InvalidName.
        """
        with pytest.raises(reflect.InvalidName):
            reflect.namedAny("twisted..internet")

    def test_module(self) -> None:
        """
        If the name is a module name, namedAny returns the module.
        """
        assert reflect.namedAny("twisted") is sys.modules["twisted"]

    def test_object(self) -> None:
        """
        If the name is an object name, namedAny returns the object.
        """
        assert reflect.namedAny("twisted.python.reflect.namedAny") is reflect.namedAny

    def test_moduleNotFound(self) -> None:
        """
        If the module is not found, namedAny raises ModuleNotFound.
        """
        with pytest.raises(reflect.ModuleNotFound):
            reflect.namedAny("twisted.moduleThatDoesNotExist")

    def test_objectNotFound(self) -> None:
        """
        If the object is not found, namedAny raises ObjectNotFound.
        """
        with pytest.raises(reflect.ObjectNotFound):
            reflect.namedAny("twisted.python.reflect.NoSuchObject")


class TestFilenameToModuleName:
    def test_module(self, tmp_path: str) -> None:
        """
        filenameToModuleName returns a module's fully-qualified name.
        """
        module = tmp_path / "foo.py"
        module.touch()
        assert reflect.filenameToModuleName(str(module)) == "foo"

    def test_package(self, tmp_path: str) -> None:
        """
        filenameToModuleName returns a package's fully-qualified name.
        """
        package = tmp_path / "foo"
        package.mkdir()
        (package / "__init__.py").touch()
        assert reflect.filenameToModuleName(str(package)) == "foo"

    def test_bytes(self, tmp_path: str) -> None:
        """
        filenameToModuleName accepts a bytes filename.
        """
        module = tmp_path / "foo.py"
        module.touch()
        assert reflect.filenameToModuleName(bytes(module)) == "foo"


class TestQual:
    def test_qual(self) -> None:
        """
        qual returns a class's fully-qualified name.
        """
        assert reflect.qual(reflect.QualTestCase) == "twisted.test.test_reflect.QualTestCase"


class TestSafeRepr:
    def test_repr(self) -> None:
        """
        safe_repr returns the result of repr().
        """
        obj = object()
        assert reflect.safe_repr(obj) == repr(obj)

    def test_safeReprOfBrokenRepr(self) -> None:
        """
        If repr() raises an exception, safe_repr returns a string containing a
        traceback.
        """

        class BrokenRepr:
            def __repr__(self) -> None:
                raise ValueError("test")

        obj = BrokenRepr()
        assert isinstance(reflect.safe_repr(obj), str)

    def test_safeReprOfBrokenReprWithBrokenClass(self) -> None:
        """
        If repr() raises an exception, and the class of the object has no
        __name__ or __str__ attribute, safe_repr returns a string containing a
        traceback.
        """
        # We need to be able to dynamically create classes which exist in
        # __main__ and not in __builtin__ when this test runs.  This is hard to
        # do, especially since this test needs to be run on Python 2.3.  So, we
        # call exec to make our class.
        exec(
            "class BrokenRepr:\n"
            "    def __repr__(self):\n"
            "        raise ValueError('test')\n"
            "    def __class__(self):\n"
            "        raise ValueError('test')\n"
            "    def __str__(self):\n"
            "        raise ValueError('test')\n"
            "obj = BrokenRepr()"
        )
        assert isinstance(reflect.safe_repr(obj), str)


class TestSafeStr:
    def test_str(self) -> None:
        """
        safe_str returns the result of str().
        """
        obj = object()
        assert reflect.safe_str(obj) == str(obj)

    def test_safeStrOfBrokenStr(self) -> None:
        """
        If str() raises an exception, safe_str returns a string containing a
        traceback.
        """

        class BrokenStr:
            def __str__(self) -> None:
                raise ValueError("test")

        obj = BrokenStr()
        assert isinstance(reflect.safe_str(obj), str)

    def test_safeStrOfBrokenStrWithBrokenClass(self) -> None:
        """
        If str() raises an exception, and the class of the object has no
        __name__ or __str__ attribute, safe_str returns a string containing a
        traceback.
        """
        # We need to be able to dynamically create classes which exist in
        # __main__ and not in __builtin__ when this test runs.  This is hard to
        # do, especially since this test needs to be run on Python 2.3.  So, we
        # call exec to make our class.
        exec(
            "class BrokenStr:\n"
            "    def __str__(self):\n"
            "        raise ValueError('test')\n"
            "    def __class__(self):\n"
            "        raise ValueError('test')\n"
            "    def __str__(self):\n"
            "        raise ValueError('test')\n"
            "obj = BrokenStr()"
        )
        assert isinstance(reflect.safe_str(obj), str)


class TestQueueMethod:
    def test_call(self) -> None:
        """
        Calling a QueueMethod adds a tuple to the list of calls.
        """
        calls: List[Tuple[str, Tuple[()]]] = []
        method = reflect.QueueMethod("method", calls)
        method()
        assert calls == [("method", ())]

    def test_callWithArgs(self) -> None:
        """
        Calling a QueueMethod with arguments adds a tuple to the list of calls.
        """
        calls: List[Tuple[str, Tuple[int]]] = []
        method = reflect.QueueMethod("method", calls)
        method(1)
        assert calls == [("method", (1,))]

    def test_callWithManyArgs(self) -> None:
        """
        Calling a QueueMethod with many arguments adds a tuple to the list of calls.
        """
        calls: List[Tuple[str, Tuple[int, int]]] = []
        method = reflect.QueueMethod("method", calls)
        method(1, 2)
        assert calls == [("method", (1, 2))]

    def test_callWithManyCalls(self) -> None:
        """
        Calling a QueueMethod multiple times adds tuples to the list of calls.
        """
        calls: List[Tuple[str, Tuple[int]]] = []
        method = reflect.QueueMethod("method", calls)
        method(1)
        method(2)
        assert calls == [("method", (1,)), ("method", (2,))]


class TestFullFuncName:
    def test_function(self) -> None:
        """
        fullFuncName returns the name of the module and the name of the function.
        """

        def func() -> None:
            pass

        assert reflect.fullFuncName(func) == __name__ + ".func"

    def test_builtin(self) -> None:
        """
        fullFuncName returns the name of a built-in function.
        """
        assert reflect.fullFuncName(len) == "builtins.len"

    def test_notFound(self) -> None:
        """
        If the function is not found, fullFuncName raises an exception.
        """
        with pytest.raises(Exception):
            reflect.fullFuncName(object)


class TestAccumulateMethods:
    def test_accumulateMethods(self) -> None:
        """
        accumulateMethods accumulates methods of an object.
        """

        class C:
            def method(self) -> None:
                pass

        obj = C()
        methods: dict[str, Callable[..., None]] = {}
        reflect.accumulateMethods(obj, methods, "method")
        assert methods == {"method": obj.method}

    def test_accumulateMethodsPrefix(self) -> None:
        """
        accumulateMethods accumulates methods of an object with a prefix.
        """

        class C:
            def prefix_method(self) -> None:
                pass

        obj = C()
        methods: dict[str, Callable[..., None]] = {}
        reflect.accumulateMethods(obj, methods, "prefix_")
        assert methods == {"method": obj.prefix_method}

    def test_accumulateMethodsInherit(self) -> None:
        """
        accumulateMethods accumulates methods of an object from a superclass.
        """

        class C:
            def method(self) -> None:
                pass

        class D(C):
            pass

        obj = D()
        methods: dict[str, Callable[..., None]] = {}
        reflect.accumulateMethods(obj, methods, "method")
        assert methods == {"method": obj.method}

    def test_accumulateMethodsOverride(self) -> None:
        """
        accumulateMethods accumulates overridden methods of an object.
        """

        class C:
            def method(self) -> None:
                pass

        class D(C):
            def method(self) -> None:
                pass

        obj = D()
        methods: dict[str, Callable[..., None]] = {}
        reflect.accumulateMethods(obj, methods, "method")
        assert methods == {"method": obj.method}

    def test_accumulateMethodsInheritPrefix(self) -> None:
        """
        accumulateMethods accumulates methods of an object from a superclass with a prefix.
        """

        class C:
            def prefix_method(self) -> None:
                pass

        class D(C):
            pass

        obj = D()
        methods: dict[str, Callable[..., None]] = {}
        reflect.accumulateMethods(obj, methods, "prefix_")
        assert methods == {"method": obj.prefix_method}

    def test_accumulateMethodsOverridePrefix(self) -> None:
        """
        accumulateMethods accumulates overridden methods of an object with a prefix.
        """

        class C:
            def prefix_method(self) -> None:
                pass

        class D(C):
            def prefix_method(self) -> None:
                pass

        obj = D()
        methods: dict[str, Callable[..., None]] = {}
        reflect.accumulateMethods(obj, methods, "prefix_")
        assert methods == {"method": obj.prefix_method}


class TestAddMethodNamesToDict:
    def test_addMethodNamesToDict(self) -> None:
        """
        addMethodNamesToDict accumulates methods of an object.
        """

        class C:
            def method(self) -> None:
                pass

        methods: dict[str, int] = {}
        reflect.addMethodNamesToDict(C, methods, "method")
        assert methods == {"": 1}

    def test_addMethodNamesToDictPrefix(self) -> None:
        """
        addMethodNamesToDict accumulates methods of an object with a prefix.
        """

        class C:
            def prefix_method(self) -> None:
                pass

        methods: dict[str, int] = {}
        reflect.addMethodNamesToDict(C, methods, "prefix_")
        assert methods == {"method": 1}

    def test_addMethodNamesToDictInherit(self) -> None:
        """
        addMethodNamesToDict accumulates methods of an object from a superclass.
        """

        class C:
            def method(self) -> None:
                pass

        class D(C):
            pass

        methods: dict[str, int] = {}
        reflect.addMethodNamesToDict(D, methods, "method")
        assert methods == {"": 1}

    def test_addMethodNamesToDictOverride(self) -> None:
        """
        addMethodNamesToDict accumulates overridden methods of an object.
        """

        class C:
            def method(self) -> None:
                pass

        class D(C):
            def method(self) -> None:
                pass

        methods: dict[str, int] = {}
        reflect.addMethodNamesToDict(D, methods, "method")
        assert methods == {"": 1}

    def test_addMethodNamesToDictInheritPrefix(self) -> None:
        """
        addMethodNamesToDict accumulates methods of an object from a superclass with a prefix.
        """

        class C:
            def prefix_method(self) -> None:
                pass

        class D(C):
            pass

        methods: dict[str, int] = {}
        reflect.addMethodNamesToDict(D, methods, "prefix_")
        assert methods == {"method": 1}

    def test_addMethodNamesToDictOverridePrefix(self) -> None:
        """
        addMethodNamesToDict accumulates overridden methods of an object with a prefix.
        """

        class C:
            def prefix_method(self) -> None:
                pass

        class D(C):
            def prefix_method(self) -> None:
                pass

        methods: dict[str, int] = {}
        reflect.addMethodNamesToDict(D, methods, "prefix_")
        assert methods == {"method": 1}


class TestAccumulateClassDict:
    def test_accumulateClassDict(self) -> None:
        """
        accumulateClassDict accumulates attributes of an object.
        """

        class C:
            attr = {"key": "value"}

        attrs: dict[str, str] = {}
        reflect.accumulateClassDict(C, "attr", attrs)
        assert attrs == {"key": "value"}

    def test_accumulateClassDictInherit(self) -> None:
        """
        accumulateClassDict accumulates attributes of an object from a superclass.
        """

        class C:
            attr = {"key": "value"}

        class D(C):
            pass

        attrs: dict[str, str] = {}
        reflect.accumulateClassDict(D, "attr", attrs)
        assert attrs == {"key": "value"}

    def test_accumulateClassDictOverride(self) -> None:
        """
        accumulateClassDict accumulates overridden attributes of an object.
        """

        class C:
            attr = {"key": "value"}

        class D(C):
            attr = {"key": "other"}

        attrs: dict[str, str] = {}
        reflect.accumulateClassDict(D, "attr", attrs)
        assert attrs == {"key": "other"}

    def test_accumulateClassDictInheritPrefix(self) -> None:
        """
        accumulateClassDict accumulates attributes of an object from a superclass with a prefix.
        """

        class C:
            prefix_attr = {"key": "value"}

        class D(C):
            pass

        attrs: dict[str, str] = {}
        reflect.accumulateClassDict(D, "prefix_attr", attrs)
        assert attrs == {"key": "value"}

    def test_accumulateClassDictOverridePrefix(self) -> None:
        """
        accumulateClassDict accumulates overridden attributes of an object with a prefix.
        """

        class C:
            prefix_attr = {"key": "value"}

        class D(C):
            prefix_attr = {"key": "other"}

        attrs: dict[str, str] = {}
        reflect.accumulateClassDict(D, "prefix_attr", attrs)
        assert attrs == {"key": "other"}


class TestAccumulateClassList:
    def test_accumulateClassList(self) -> None:
        """
        accumulateClassList accumulates attributes of an object.
        """

        class C:
            attr = ["value"]

        attrs: list[str] = []
        reflect.accumulateClassList(C, "attr", attrs)
        assert attrs == ["value"]

    def test_accumulateClassListInherit(self) -> None:
        """
        accumulateClassList accumulates attributes of an object from a superclass.
        """

        class C:
            attr = ["value"]

        class D(C):
            pass

        attrs: list[str] = []
        reflect.accumulateClassList(D, "attr", attrs)
        assert attrs == ["value"]

    def test_accumulateClassListOverride(self) -> None:
        """
        accumulateClassList accumulates overridden attributes of an object.
        """

        class C:
            attr = ["value"]

        class D(C):
            attr = ["other"]

        attrs: list[str] = []
        reflect.accumulateClassList(D, "attr", attrs)
        assert attrs == ["value", "other"]

    def test_accumulateClassListInheritPrefix(self) -> None:
        """
        accumulateClassList accumulates attributes of an object from a superclass with a prefix.
        """

        class C:
            prefix_attr = ["value"]

        class D(C):
            pass

        attrs: list[str] = []
        reflect.accumulateClassList(D, "prefix_attr", attrs)
        assert attrs == ["value"]

    def test_accumulateClassListOverridePrefix(self) -> None:
        """
        accumulateClassList accumulates overridden attributes of an object with a prefix.
        """

        class C:
            prefix_attr = ["value"]

        class D(C):
            prefix_attr = ["other"]

        attrs: list[str] = []
        reflect.accumulateClassList(D, "prefix_attr", attrs)
        assert attrs == ["value", "other"]


class TestFindInstances:
    def test_findInstances(self) -> None:
        """
        findInstances returns instances of a given class.
        """
        obj = object()
        assert list(reflect.findInstances(obj, object)) == [""]


class TestModgrep:
    def test_modgrep(self) -> None:
        """
        modgrep searches for modules.
        """
        assert list(reflect.modgrep("twisted")) == ["['twisted']"]