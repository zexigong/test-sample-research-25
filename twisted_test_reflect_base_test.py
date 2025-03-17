import pytest
import types
import os
import sys
import weakref
from collections import deque
from twisted.python.reflect import (
    InvalidName,
    ModuleNotFound,
    ObjectNotFound,
    prefixedMethodNames,
    addMethodNamesToDict,
    prefixedMethods,
    accumulateMethods,
    namedModule,
    namedObject,
    requireModule,
    namedAny,
    filenameToModuleName,
    qual,
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

class TestReflect:

    def test_prefixedMethodNames(self):
        class TestClass:
            def prefix_method1(self): pass
            def prefix_method2(self): pass
            def other_method(self): pass

        assert prefixedMethodNames(TestClass, 'prefix_') == ['method1', 'method2']

    def test_addMethodNamesToDict(self):
        class TestClass:
            def prefix_method1(self): pass
            def prefix_method2(self): pass
            def other_method(self): pass

        methods_dict = {}
        addMethodNamesToDict(TestClass, methods_dict, 'prefix_')
        assert methods_dict == {'method1': 1, 'method2': 1}

    def test_prefixedMethods(self):
        class TestClass:
            def prefix_method1(self): pass
            def prefix_method2(self): pass
            def other_method(self): pass

        obj = TestClass()
        methods = prefixedMethods(obj, 'prefix_')
        assert len(methods) == 2
        assert all(callable(m) for m in methods)

    def test_accumulateMethods(self):
        class TestClass:
            def prefix_method1(self): pass
            def prefix_method2(self): pass
            def other_method(self): pass

        obj = TestClass()
        methods_dict = {}
        accumulateMethods(obj, methods_dict, 'prefix_')
        assert len(methods_dict) == 2
        assert all(callable(m) for m in methods_dict.values())

    def test_namedModule(self):
        assert namedModule('os') is os

    def test_namedObject(self):
        assert namedObject('os.path') is os.path

    def test_requireModule(self):
        assert requireModule('os') is os
        assert requireModule('non_existent_module', default='default') == 'default'

    def test_namedAny(self):
        assert namedAny('os.path') is os.path
        with pytest.raises(InvalidName):
            namedAny('')
        with pytest.raises(ModuleNotFound):
            namedAny('non_existent_module')
        with pytest.raises(ObjectNotFound):
            namedAny('os.non_existent_object')

    def test_filenameToModuleName(self):
        assert filenameToModuleName('/path/to/twisted/test_reflect.py') == 'twisted.test_reflect'

    def test_qual(self):
        assert qual(types.FunctionType) == 'types.FunctionType'

    def test_safe_repr(self):
        class BadRepr:
            def __repr__(self):
                raise ValueError("bad repr")
        assert "bad repr" in safe_repr(BadRepr())

    def test_safe_str(self):
        class BadStr:
            def __str__(self):
                raise ValueError("bad str")
        assert "bad str" in safe_str(BadStr())

    def test_fullFuncName(self):
        def sample_function(): pass
        assert fullFuncName(sample_function) == __name__ + '.sample_function'

    def test_getClass(self):
        assert getClass(5) is int

    def test_accumulateClassDict(self):
        class Base:
            props = {'a': 1}
        class Derived(Base):
            props = {'b': 2}

        d = {}
        accumulateClassDict(Derived, 'props', d)
        assert d == {'a': 1, 'b': 2}

    def test_accumulateClassList(self):
        class Base:
            props = [1]
        class Derived(Base):
            props = [2]

        l = []
        accumulateClassList(Derived, 'props', l)
        assert l == [1, 2]

    def test_isSame(self):
        a = b = object()
        assert isSame(a, b)
        assert not isSame(a, object())

    def test_isLike(self):
        assert isLike(1, 1)
        assert not isLike(1, 2)

    def test_modgrep(self):
        # This will depend on the environment
        assert isinstance(modgrep('sys'), list)

    def test_isOfType(self):
        assert isOfType(1, int)
        assert not isOfType(1, str)

    def test_findInstances(self):
        assert isinstance(findInstances(sys.modules, type(sys)), list)