import tempfile
import os
from datetime import date, datetime
from decimal import Decimal
from collections import namedtuple

import pytest

import hug

from hug.output_format import (
    IMAGE_TYPES,
    VIDEO_TYPES,
    file,
    json,
    json_camelcase,
    on_valid,
    pretty_json,
    suffix,
    html,
    json_convert,
    json_converters,
    _json_converter,
)


def test_json():
    """Ensure that the built-in JSON handler encodes as expected"""
    assert json({"a": "b"}) == b'{"a":"b"}'
    assert json({"a": date(year=2016, month=10, day=21)}) == b'{"a":"2016-10-21"}'
    assert json({"a": datetime(year=2016, month=10, day=21, hour=10, minute=40)}) == b'{"a":"2016-10-21T10:40:00"}'
    assert json({"a": Decimal(1.1)}) == b'{"a":"1.1"}'
    assert json(namedtuple("toy", ("a", "b"))("a", "b")) == b'{"a":"a","b":"b"}'
    assert json(namedtuple("toy", ("a", "b"))("a", "b"), ensure_ascii=True) == b'{"a":"a","b":"b"}'
    assert json(namedtuple("toy", ("a", "b"))("a", "b"), ensure_ascii=False) == b'{"a":"a","b":"b"}'
    assert json(namedtuple("toy", ("a", "b"))("a", "b"), ensure_ascii=True, foo="bar") == b'{"a":"a","b":"b"}'
    assert json(namedtuple("toy", ("a", "b"))("a", "b"), ensure_ascii=False, foo="bar") == b'{"a":"a","b":"b"}'
    assert json(namedtuple("toy", ("a", "b"))("a", "b"), foo="bar") == b'{"a":"a","b":"b"}'

    assert json.content_type == "application/json; charset=utf-8"


def test_json_camelcase():
    """Ensure that the built-in JSON handler encodes as expected"""
    assert json_camelcase({"a": "b"}) == b'{"a":"b"}'
    assert json_camelcase({"a_b": "b"}) == b'{"aB":"b"}'
    assert json_camelcase({"a_b": "b", "c": {"d_e": "f"}}) == b'{"aB":"b","c":{"dE":"f"}}'
    assert json_camelcase([{"a_b": "b"}, {"c": {"d_e": "f"}}]) == b'[{"aB":"b"},{"c":{"dE":"f"}}]'
    assert json_camelcase([{"a_b": "b"}, {"c": {"d_e": "f"}}], ensure_ascii=True) == b'[{"aB":"b"},{"c":{"dE":"f"}}]'
    assert json_camelcase([{"a_b": "b"}, {"c": {"d_e": "f"}}], ensure_ascii=False) == b'[{"aB":"b"},{"c":{"dE":"f"}}]'
    assert json_camelcase([{"a_b": "b"}, {"c": {"d_e": "f"}}], ensure_ascii=True, foo="bar") == b'[{"aB":"b"},{"c":{"dE":"f"}}]'
    assert json_camelcase([{"a_b": "b"}, {"c": {"d_e": "f"}}], ensure_ascii=False, foo="bar") == b'[{"aB":"b"},{"c":{"dE":"f"}}]'
    assert json_camelcase([{"a_b": "b"}, {"c": {"d_e": "f"}}], foo="bar") == b'[{"aB":"b"},{"c":{"dE":"f"}}]'

    assert json_camelcase.content_type == "application/json; charset=utf-8"


def test_pretty_json():
    """Ensure that the built-in JSON handler encodes as expected"""
    assert pretty_json({"a": "b"}) == b'{\n    "a": "b"\n}'
    assert pretty_json.content_type == "application/json; charset=utf-8"


def test_html():
    """Ensure that the built-in HTML handler encodes as expected"""
    assert html({"a": "b"}) == b"{'a': 'b'}"
    assert html.content_type == "text/html; charset=utf-8"


def test_file():
    """Ensure that the built-in file handler returns the correct file"""
    with tempfile.NamedTemporaryFile(delete=False) as temporary_file:
        temporary_file.write(b"Hello World!")

    assert file(temporary_file.name).read() == b"Hello World!"
    assert file(None) == ""
    assert file.content_type == "file/dynamic"
    os.unlink(temporary_file.name)


def test_suffix():
    """Ensure that the suffix based output format works as expected"""
    suffix_formatter = suffix({".js": json, ".html": html}, default=json)
    assert suffix_formatter({"a": "b"}, hug.Request("/path.js"), hug.Response()) == b'{"a":"b"}'
    assert suffix_formatter({"a": "b"}, hug.Request("/path.html"), hug.Response()) == b"{'a': 'b'}"
    assert suffix_formatter({"a": "b"}, hug.Request("/path"), hug.Response()) == b'{"a":"b"}'
    with pytest.raises(hug.HTTPNotAcceptable):
        suffix_formatter({"a": "b"}, hug.Request("/path.xml"), hug.Response())


def test_json_convert():
    class TestClass:
        def __init__(self):
            self.value = 2.5

    @json_convert(TestClass)
    def _json_converter(item):
        return item.value

    instance = TestClass()
    assert _json_converter(instance) == 2.5

    del json_converters[TestClass]


def test_json_converter():
    """Ensure that the JSON converter correctly handles all built-in types"""
    class Custom:
        def __native_types__(self):
            return 1

    assert _json_converter(Custom()) == 1

    class CustomWithNoNative:
        pass

    with pytest.raises(TypeError):
        _json_converter(CustomWithNoNative())


def test_image_handlers():
    """Ensure that all image handlers are defined and callable"""
    for image_type in IMAGE_TYPES:
        assert hasattr(hug.output_format, "{0}_image".format(image_type.replace("+", "_")))


def test_video_handlers():
    """Ensure that all video handlers are defined and callable"""
    for video_type, _ in VIDEO_TYPES:
        assert hasattr(hug.output_format, "{0}_video".format(video_type))


def test_on_valid():
    """Ensure the on_valid output format correctly renders the expected output format"""
    @on_valid("application/custom")
    def custom(content, **kwargs):
        return "CUSTOM"

    assert custom({"a": "b"}, hug.Response()) == "CUSTOM"
    assert custom({"errors": "b"}, hug.Response()) == b'{"errors":"b"}'
    assert custom.content_type == "application/custom"

    class CustomObject:
        pass

    @on_valid("application/custom")
    def custom(content, **kwargs):
        return "CUSTOM"

    assert custom(CustomObject(), hug.Response()) == "CUSTOM"