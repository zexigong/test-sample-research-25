import pytest
from unittest.mock import Mock
from hug.route import Object, API
from falcon import HTTP_METHODS


@pytest.fixture
def mock_function():
    def func():
        pass
    return func


@pytest.fixture
def mock_class():
    class MockClass:
        def get(self):
            pass

        def post(self):
            pass

    return MockClass


def test_object_initialization():
    router = Object(urls="/test", accept=("GET",))
    assert router.route["urls"] == "/test"
    assert router.route["accept"] == ("GET",)


def test_object_call_method_function(mock_function):
    router = Object(urls="/test", accept=("GET",))
    wrapped_function = router(mock_function)
    assert hasattr(wrapped_function, "_hug_http_routes")
    assert wrapped_function._hug_http_routes == [router.route]


def test_object_call_method_class(mock_class):
    router = Object(urls="/test", accept=("GET",))
    wrapped_class = router(mock_class)
    assert hasattr(wrapped_class.get, "_hug_http_routes")
    assert wrapped_class.get._hug_http_routes == [router.route]
    assert hasattr(wrapped_class.post, "_hug_http_routes")
    assert wrapped_class.post._hug_http_routes == [router.route]


def test_object_http_methods(mock_class):
    router = Object(urls="/test", accept=("GET",))
    decorated_class = router.http_methods()(mock_class)
    instance = decorated_class()

    assert hasattr(instance.get, "_hug_http_routes")
    assert hasattr(instance.post, "_hug_http_routes")


def test_api_initialization():
    api = API("test_api")
    assert api.name == "test_api"
    assert api.module is None


def test_api_http_method():
    api = API("test_api")
    route = api.http(urls="/test", accept=("GET",))
    assert route.route["urls"] == "/test"
    assert route.route["accept"] == ("GET",)
    assert route.route["api"] == api


def test_api_cli_method(mock_function):
    api = API("test_api")
    cli_route = api.cli(mock_function)
    assert cli_route.route["api"] == api


def test_api_exception_method(mock_function):
    api = API("test_api")
    exception_route = api.exception(mock_function)
    assert exception_route.route["api"] == api


def test_api_object_method(mock_class):
    api = API("test_api")
    object_route = api.object(mock_class)
    assert object_route.route["api"] == api


def test_api_get_method():
    api = API("test_api")
    get_route = api.get(urls="/get_test")
    assert get_route.route["urls"] == "/get_test"
    assert get_route.route["accept"] == ("GET",)
    assert get_route.route["api"] == api


def test_api_post_method():
    api = API("test_api")
    post_route = api.post(urls="/post_test")
    assert post_route.route["urls"] == "/post_test"
    assert post_route.route["accept"] == ("POST",)
    assert post_route.route["api"] == api


def test_api_put_method():
    api = API("test_api")
    put_route = api.put(urls="/put_test")
    assert put_route.route["urls"] == "/put_test"
    assert put_route.route["accept"] == ("PUT",)
    assert put_route.route["api"] == api


def test_api_delete_method():
    api = API("test_api")
    delete_route = api.delete(urls="/delete_test")
    assert delete_route.route["urls"] == "/delete_test"
    assert delete_route.route["accept"] == ("DELETE",)
    assert delete_route.route["api"] == api


def test_api_connect_method():
    api = API("test_api")
    connect_route = api.connect(urls="/connect_test")
    assert connect_route.route["urls"] == "/connect_test"
    assert connect_route.route["accept"] == ("CONNECT",)
    assert connect_route.route["api"] == api


def test_api_head_method():
    api = API("test_api")
    head_route = api.head(urls="/head_test")
    assert head_route.route["urls"] == "/head_test"
    assert head_route.route["accept"] == ("HEAD",)
    assert head_route.route["api"] == api


def test_api_options_method():
    api = API("test_api")
    options_route = api.options(urls="/options_test")
    assert options_route.route["urls"] == "/options_test"
    assert options_route.route["accept"] == ("OPTIONS",)
    assert options_route.route["api"] == api


def test_api_patch_method():
    api = API("test_api")
    patch_route = api.patch(urls="/patch_test")
    assert patch_route.route["urls"] == "/patch_test"
    assert patch_route.route["accept"] == ("PATCH",)
    assert patch_route.route["api"] == api


def test_api_trace_method():
    api = API("test_api")
    trace_route = api.trace(urls="/trace_test")
    assert trace_route.route["urls"] == "/trace_test"
    assert trace_route.route["accept"] == ("TRACE",)
    assert trace_route.route["api"] == api


def test_api_get_post_method():
    api = API("test_api")
    get_post_route = api.get_post(urls="/get_post_test")
    assert get_post_route.route["urls"] == "/get_post_test"
    assert get_post_route.route["accept"] == ("GET", "POST")
    assert get_post_route.route["api"] == api


def test_api_put_post_method():
    api = API("test_api")
    put_post_route = api.put_post(urls="/put_post_test")
    assert put_post_route.route["urls"] == "/put_post_test"
    assert put_post_route.route["accept"] == ("PUT", "POST")
    assert put_post_route.route["api"] == api