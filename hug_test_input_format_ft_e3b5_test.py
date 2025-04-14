import json

import pytest

import hug
from hug import input_format


def test_json():
    """Test to ensure the JSON input format correctly loads any passed in data"""
    assert input_format.json('{"a": "b"}') == {"a": "b"}
    assert input_format.json(b'{"a": "b"}') == {"a": "b"}
    with pytest.raises(ValueError):
        input_format.json("a")


def test_json_body():
    """Test to ensure the JSON input format correctly loads any passed in data"""
    assert input_format.json_body('{"a": "b"}') == {"a": "b"}
    assert input_format.json_body(b'{"a": "b"}') == {"a": "b"}
    with pytest.raises(ValueError):
        input_format.json_body("a")


def test_json_module():
    """Test to ensure the JSON input format correctly loads any passed in data"""
    assert input_format.json_module('{"a": "b"}') == {"a": "b"}
    assert input_format.json_module(b'{"a": "b"}') == {"a": "b"}
    with pytest.raises(ValueError):
        input_format.json_module("a")


def test_json_module_body():
    """Test to ensure the JSON input format correctly loads any passed in data"""
    assert input_format.json_module_body('{"a": "b"}') == {"a": "b"}
    assert input_format.json_module_body(b'{"a": "b"}') == {"a": "b"}
    with pytest.raises(ValueError):
        input_format.json_module_body("a")


def test_query():
    """Test to ensure the query format correctly parses query strings"""
    assert input_format.query("a=b") == {"a": "b"}
    assert input_format.query("a=b&c=d") == {"a": "b", "c": "d"}
    assert input_format.query("a=b&c=d&a=c") == {"a": ["b", "c"], "c": "d"}
    assert input_format.query("a=b&c=d&a=c", single=False) == {
        "a": ["b", "c"],
        "c": ["d"],
    }
    assert input_format.query("a=b&c=d&a=c", single=True) == {"a": "c", "c": "d"}
    assert input_format.query("a=b&c=d&a=c&d=e", single=["a", "d"]) == {
        "a": "c",
        "c": ["d"],
        "d": "e",
    }
    assert input_format.query("a=b&c=d&a=c&d=e", single={"a": 1, "d": 1}) == {
        "a": "c",
        "c": ["d"],
        "d": "e",
    }
    assert input_format.query("a=b&c=d&a=c&d=e", single={"a": False, "d": 1}) == {
        "a": ["b", "c"],
        "c": ["d"],
        "d": "e",
    }

    assert input_format.query("a=b&c=d&a=c", single=True, list=False) == {
        "a": "b",
        "c": "d",
    }
    assert input_format.query("a=b&c=d&a=c", single=False, list=False) == {
        "a": "b",
        "c": "d",
    }
    assert input_format.query("a=b&c=d&a=c", single=False, list=["a"]) == {
        "a": ["b", "c"],
        "c": "d",
    }
    assert input_format.query("a=b&c=d&a=c", single=False, list={"a": 1}) == {
        "a": ["b", "c"],
        "c": "d",
    }
    assert input_format.query("a=b&c=d&a=c", single=False, list={"a": True}) == {
        "a": ["b", "c"],
        "c": "d",
    }
    assert input_format.query("a=b&c=d&a=c", single=False, list={"a": False}) == {
        "a": "b",
        "c": "d",
    }


def test_multipart():
    """Test to ensure the multipart input format correctly parses multipart encoded strings"""
    input_data = b"\r\n".join(
        (
            b"-----------------------------9051914041544843365972754266",
            b"Content-Disposition: form-data; name=\"text\"",
            b"",
            b"test",
            b"-----------------------------9051914041544843365972754266",
            b"Content-Disposition: form-data; name=\"file1\"; filename=\"a.txt\"",
            b"Content-Type: text/plain",
            b"",
            b"Content of a.txt.",
            b"-----------------------------9051914041544843365972754266",
            b"Content-Disposition: form-data; name=\"file2\"; filename=\"a.html\"",
            b"Content-Type: text/html",
            b"",
            b"<!DOCTYPE html><title>Content of a.html.</title>",
            b"-----------------------------9051914041544843365972754266--",
            b"",
        )
    )
    assert input_format.multipart(
        input_data,
        "---------------------------9051914041544843365972754266",
        headers={"Content-Type": "multipart/form-data"},
    ) == {
        "text": "test",
        "file1": hug.types.text("Content of a.txt."),
        "file2": hug.types.text("<!DOCTYPE html><title>Content of a.html.</title>"),
    }


def test_multipart_with_file():
    """Test to ensure the multipart input format correctly parses multipart encoded strings"""
    input_data = b"\r\n".join(
        (
            b"-----------------------------9051914041544843365972754266",
            b"Content-Disposition: form-data; name=\"text\"",
            b"",
            b"test",
            b"-----------------------------9051914041544843365972754266",
            b"Content-Disposition: form-data; name=\"file1\"; filename=\"a.txt\"",
            b"Content-Type: text/plain",
            b"",
            b"Content of a.txt.",
            b"-----------------------------9051914041544843365972754266",
            b"Content-Disposition: form-data; name=\"file2\"; filename=\"a.html\"",
            b"Content-Type: text/html",
            b"",
            b"<!DOCTYPE html><title>Content of a.html.</title>",
            b"-----------------------------9051914041544843365972754266--",
            b"",
        )
    )
    assert input_format.multipart(
        input_data,
        "---------------------------9051914041544843365972754266",
        headers={"Content-Type": "multipart/form-data"},
        files=True,
    ) == {
        "text": "test",
        "file1": ("a.txt", "Content of a.txt."),
        "file2": ("a.html", "<!DOCTYPE html><title>Content of a.html.</title>"),
    }


def test_text():
    """Test to ensure the text input format returns exactly what was passed in"""
    assert input_format.text("test") == "test"


def test_plain_text():
    """Test to ensure the plain text input format returns exactly what was passed in"""
    assert input_format.plain_text("test") == "test"


def test_html():
    """Test to ensure the HTML input format returns exactly what was passed in"""
    assert input_format.html("test") == "test"


def test_html_body():
    """Test to ensure the HTML input format returns exactly what was passed in"""
    assert input_format.html_body("test") == "test"