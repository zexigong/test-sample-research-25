import asyncio
import os
from datetime import date, datetime
from types import MethodType

import falcon
import pytest

import hug
from hug import routing


def test_cli_function():
    """Test to ensure that a function can be exposed via the CLI router"""
    @hug.cli()
    def hello_world():
        return "Hello World!"

    assert hug.test.cli(hello_world) == "Hello World!"


def test_cli_function_named():
    """Test to ensure that a function can be exposed via the CLI router with a custom name"""
    @hug.cli(name="hello")
    def hello_world():
        return "Hello World!"

    assert hug.test.cli(hello_world, "hello") == "Hello World!"


def test_cli_function_named_with_docstring():
    """Test to ensure that a function can be exposed via the CLI router with a custom name and a docstring"""
    @hug.cli(name="hello")
    def hello_world():
        """A docstring for the hello_world function"""
        return "Hello World!"

    assert hug.test.cli(hello_world, "hello") == "Hello World!"


def test_cli_function_custom_docstring():
    """Test to ensure that a function can be exposed via the CLI router with a custom docstring"""
    @hug.cli(doc="Custom Docstring")
    def hello_world():
        """A docstring for the hello_world function"""
        return "Hello World!"

    assert hug.test.cli(hello_world) == "Hello World!"


def test_cli_function_with_input():
    """Test to ensure that a function can be exposed via the CLI router with an input type"""
    @hug.cli()
    def hello_world(name: str):
        return f"Hello {name}!"

    assert hug.test.cli(hello_world, "World") == "Hello World!"


def test_cli_function_with_input_and_output():
    """Test to ensure that a function can be exposed via the CLI router with an input and output type"""
    @hug.cli()
    def hello_world(name: str) -> str:
        return f"Hello {name}!"

    assert hug.test.cli(hello_world, "World") == "Hello World!"


def test_local_function():
    """Test to ensure that a function can be exposed via the local router"""
    @hug.local()
    def hello_world():
        return "Hello World!"

    assert hello_world() == "Hello World!"


def test_local_function_with_input():
    """Test to ensure that a function can be exposed via the local router with an input type"""
    @hug.local()
    def hello_world(name: str):
        return f"Hello {name}!"

    assert hello_world("World") == "Hello World!"


def test_local_function_with_input_and_output():
    """Test to ensure that a function can be exposed via the local router with an input and output type"""
    @hug.local()
    def hello_world(name: str) -> str:
        return f"Hello {name}!"

    assert hello_world("World") == "Hello World!"


def test_http_function():
    """Test to ensure that a function can be exposed via the HTTP router"""
    @hug.get()
    def hello_world():
        return "Hello World!"

    assert hug.test.get(hello_world) == b"Hello World!"


def test_http_function_with_input():
    """Test to ensure that a function can be exposed via the HTTP router with an input type"""
    @hug.get()
    def hello_world(name: str):
        return f"Hello {name}!"

    assert hug.test.get(hello_world, name="World") == b"Hello World!"


def test_http_function_with_input_and_output():
    """Test to ensure that a function can be exposed via the HTTP router with an input and output type"""
    @hug.get()
    def hello_world(name: str) -> str:
        return f"Hello {name}!"

    assert hug.test.get(hello_world, name="World") == b"Hello World!"


def test_not_found_function():
    """Test to ensure that a function can be exposed via the not found router"""
    @hug.not_found()
    def not_found():
        return "Not Found!"

    assert hug.test.get(not_found) == b"Not Found!"


def test_sink_function():
    """Test to ensure that a function can be exposed via the sink router"""
    @hug.sink()
    def sink(request, response, *args, **kwargs):
        return "Sink!"

    assert hug.test.get(sink) == b"Sink!"


def test_static_function():
    """Test to ensure that a function can be exposed via the static router"""
    @hug.static()
    def static():
        return "Static!"

    assert hug.test.get(static) == b"Static!"


def test_exception_function():
    """Test to ensure that a function can be exposed via the exception router"""
    @hug.exception()
    def exception():
        return "Exception!"

    assert hug.test.get(exception) == b"Exception!"


def test_url_router():
    """Test to ensure that the URL router can be used to route a URL to a function"""
    @hug.get("/hello")
    def hello_world():
        return "Hello World!"

    assert hug.test.get(hello_world) == b"Hello World!"


def test_url_router_with_input():
    """Test to ensure that the URL router can be used to route a URL to a function with an input type"""
    @hug.get("/hello")
    def hello_world(name: str):
        return f"Hello {name}!"

    assert hug.test.get(hello_world, name="World") == b"Hello World!"


def test_url_router_with_input_and_output():
    """Test to ensure that the URL router can be used to route a URL to a function with an input and output type"""
    @hug.get("/hello")
    def hello_world(name: str) -> str:
        return f"Hello {name}!"

    assert hug.test.get(hello_world, name="World") == b"Hello World!"


def test_http_router_with_input():
    """Test to ensure that the HTTP router can be used to route a URL to a function with an input type"""
    @hug.http("/hello")
    def hello_world(name: str):
        return f"Hello {name}!"

    assert hug.test.get(hello_world, name="World") == b"Hello World!"


def test_http_router_with_input_and_output():
    """Test to ensure that the HTTP router can be used to route a URL to a function with an input and output type"""
    @hug.http("/hello")
    def hello_world(name: str) -> str:
        return f"Hello {name}!"

    assert hug.test.get(hello_world, name="World") == b"Hello World!"