import pytest
from types import MethodType
from hug.introspect import (
    is_method,
    is_coroutine,
    name,
    arguments,
    takes_kwargs,
    takes_args,
    takes_arguments,
    takes_all_arguments,
    generate_accepted_kwargs,
)

# Helper functions for testing
def sample_function(arg1, arg2, *args, **kwargs):
    pass

class SampleClass:
    def method(self):
        pass

    async def async_method(self):
        pass

def coroutine_function():
    pass
coroutine_function._is_coroutine = True


# Tests
def test_is_method():
    assert is_method(SampleClass().method) is True
    assert is_method(sample_function) is False

def test_is_coroutine():
    assert is_coroutine(SampleClass().async_method) is True
    assert is_coroutine(coroutine_function) is True
    assert is_coroutine(sample_function) is False

def test_name():
    assert name(sample_function) == "sample_function"
    assert name(SampleClass().method) == "method"

def test_arguments():
    assert arguments(sample_function) == ("arg1", "arg2")
    assert arguments(SampleClass().method) == ("self",)

def test_takes_kwargs():
    assert takes_kwargs(sample_function) is True
    assert takes_kwargs(SampleClass().method) is False

def test_takes_args():
    assert takes_args(sample_function) is True
    assert takes_args(SampleClass().method) is False

def test_takes_arguments():
    assert takes_arguments(sample_function, "arg1", "arg2", "arg3") == {"arg1", "arg2"}
    assert takes_arguments(SampleClass().method, "self") == {"self"}

def test_takes_all_arguments():
    assert takes_all_arguments(sample_function, "arg1", "arg2") is True
    assert takes_all_arguments(sample_function, "arg1", "arg3") is False

def test_generate_accepted_kwargs():
    accepted_kwargs = generate_accepted_kwargs(sample_function, "arg1", "arg2", "arg3")
    assert accepted_kwargs({"arg1": 1, "arg2": 2, "arg3": 3, "arg4": 4}) == {"arg1": 1, "arg2": 2}

    accepted_kwargs_no_kwargs = generate_accepted_kwargs(SampleClass().method, "self", "arg2")
    assert accepted_kwargs_no_kwargs({"self": 1, "arg2": 2, "arg3": 3}) == {"self": 1}