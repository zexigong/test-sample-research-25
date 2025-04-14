from hug import introspect


def test_is_method():
    """Test to ensure that is_method correctly detects methods"""
    assert introspect.is_method(test_is_method)
    assert not introspect.is_method(introspect.is_method)


def test_is_coroutine():
    """Test to ensure that is_coroutine correctly detects coroutines"""

    async def coroutine():
        pass

    assert introspect.is_coroutine(coroutine)
    assert not introspect.is_coroutine(introspect.is_method)


def test_name():
    """Test to ensure that name can correctly identify a function's name"""
    assert introspect.name(test_name) == "test_name"
    assert introspect.name(introspect.is_method) == "is_method"


def test_arguments():
    """Test to ensure that arguments correctly returns a tuple of all a function's arguments"""
    assert introspect.arguments(test_arguments) == ()
    assert introspect.arguments(introspect.is_coroutine) == ("function",)


def test_takes_kwargs():
    """Test to ensure that takes_kwargs correctly identifies functions that accept arbitrary keyword arguments"""

    def no_kwargs():
        pass

    def with_kwargs(**kwargs):
        pass

    assert not introspect.takes_kwargs(no_kwargs)
    assert introspect.takes_kwargs(with_kwargs)


def test_takes_args():
    """Test to ensure that takes_args correctly identifies functions that accept arbitrary arguments"""

    def no_args():
        pass

    def with_args(*args):
        pass

    assert not introspect.takes_args(no_args)
    assert introspect.takes_args(with_args)


def test_takes_arguments():
    """Test to ensure that takes_arguments correctly identifies if a function takes a given argument"""

    def one_argument(name):
        pass

    def two_arguments(name, age):
        pass

    assert not introspect.takes_arguments(one_argument, "age")
    assert not introspect.takes_arguments(one_argument, "age", "height")
    assert introspect.takes_arguments(one_argument, "name")
    assert introspect.takes_arguments(two_arguments, "name")
    assert introspect.takes_arguments(two_arguments, "name", "height")
    assert introspect.takes_arguments(two_arguments, "name", "age")


def test_takes_all_arguments():
    """Test to ensure that takes_all_arguments correctly identifies if a function takes ALL given arguments"""

    def one_argument(name):
        pass

    def two_arguments(name, age):
        pass

    assert not introspect.takes_all_arguments(one_argument, "age")
    assert not introspect.takes_all_arguments(one_argument, "age", "height")
    assert introspect.takes_all_arguments(one_argument, "name")
    assert introspect.takes_all_arguments(two_arguments, "name")
    assert not introspect.takes_all_arguments(two_arguments, "name", "height")
    assert introspect.takes_all_arguments(two_arguments, "name", "age")


def test_generate_accepted_kwargs():
    """Test to ensure that generate_accepted_kwargs creates a function which returns only valid kwargs for a given
       function
    """

    def two_arguments(name, age):
        pass

    def two_arguments_plus_kwargs(name, age, **kwargs):
        pass

    accepted_kwargs = introspect.generate_accepted_kwargs(two_arguments, "name", "age", "height")
    assert accepted_kwargs({"name": "timothy", "age": 30, "height": 180}) == {"name": "timothy", "age": 30}
    accepted_kwargs = introspect.generate_accepted_kwargs(two_arguments_plus_kwargs, "name", "age", "height")
    assert accepted_kwargs({"name": "timothy", "age": 30, "height": 180}) == {
        "name": "timothy",
        "age": 30,
        "height": 180,
    }