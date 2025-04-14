import pytest
from datetime import datetime, date, timedelta
from decimal import Decimal
from uuid import UUID
from io import BytesIO
import base64
import os

import hug.output_format as output_format

try:
    import numpy
except ImportError:
    numpy = False

class MockRequest:
    def __init__(self, accept="", content_type=""):
        self.accept = accept
        self.content_type = content_type
        self.path = ""

class MockResponse:
    def __init__(self):
        self.content_type = ""
        self.status = ""

def test_json_basic():
    assert output_format.json({"key": "value"}) == b'{"key":"value"}'

def test_json_tuple():
    from collections import namedtuple
    Point = namedtuple('Point', ['x', 'y'])
    point = Point(11, y=22)
    assert output_format.json(point) == b'{"x":11,"y":22}'

def test_json_date():
    assert output_format.json({"date": datetime(2023, 1, 1)}) == b'{"date":"2023-01-01T00:00:00"}'

def test_json_bytes():
    assert output_format.json(b"hello") == b'"aGVsbG8="'  # base64 encoded

def test_json_decimal():
    assert output_format.json(Decimal("10.5")) == b'"10.5"'

def test_json_uuid():
    assert output_format.json(UUID("12345678123456781234567812345678")) == b'"12345678-1234-5678-1234-567812345678"'

def test_json_timedelta():
    assert output_format.json(timedelta(days=1, hours=2)) == b'90000.0'

def test_json_numpy():
    if not numpy:
        pytest.skip("Numpy not installed")

    array = numpy.array([1, 2, 3])
    assert output_format.json(array) == b'[1,2,3]'

def test_text():
    assert output_format.text("Hello, World!") == b"Hello, World!"

def test_html():
    assert output_format.html("<h1>Hello</h1>") == b"<h1>Hello</h1>"

def test_json_camelcase():
    assert output_format.json_camelcase({"snake_case": "value"}) == b'{"snakeCase":"value"}'

def test_pretty_json():
    assert (
        output_format.pretty_json({"key": "value"})
        == b'{\n    "key": "value"\n}'
    )

def test_image_handler():
    handler = output_format.png_image
    mock_data = BytesIO(b"fakeimagecontent")
    mock_data.name = "fakeimage.png"
    response = MockResponse()
    result = handler(mock_data, response=response)
    assert result.read() == b"fakeimagecontent"

def test_video_handler():
    handler = output_format.mp4_video
    mock_data = BytesIO(b"fakevideocontent")
    mock_data.name = "fakevideo.mp4"
    response = MockResponse()
    result = handler(mock_data, response=response)
    assert result.read() == b"fakevideocontent"

def test_file_handler():
    response = MockResponse()
    with open("test.txt", "wb") as f:
        f.write(b"file content")
    result = output_format.file("test.txt", response=response)
    assert result.read() == b"file content"
    os.remove("test.txt")

def test_accept_quality():
    assert output_format.accept_quality("text/html;q=0.9") == (0.9, "text/html")

def test_on_content_type():
    handler = output_format.on_content_type({"application/json": output_format.json})
    data = {"key": "value"}
    request = MockRequest(content_type="application/json")
    response = MockResponse()
    result = handler(data, request, response)
    assert result == b'{"key":"value"}'
    assert response.content_type == "application/json; charset=utf-8"

def test_on_valid():
    @output_format.on_valid("application/json")
    def mock_handler(data, request=None, response=None):
        return {"status": "valid"}

    data = {"errors": "something went wrong"}
    response = MockResponse()
    result = mock_handler(data, response=response)
    assert result == b'{"errors":"something went wrong"}'
    assert response.content_type == "application/json; charset=utf-8"

def test_suffix():
    handler = output_format.suffix({".json": output_format.json})
    data = {"key": "value"}
    request = MockRequest()
    request.path = "/test.json"
    response = MockResponse()
    result = handler(data, request, response)
    assert result == b'{"key":"value"}'
    assert response.content_type == "application/json; charset=utf-8"

def test_prefix():
    handler = output_format.prefix({"/json": output_format.json})
    data = {"key": "value"}
    request = MockRequest()
    request.path = "/json/test"
    response = MockResponse()
    result = handler(data, request, response)
    assert result == b'{"key":"value"}'
    assert response.content_type == "application/json; charset=utf-8"