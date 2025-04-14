import pytest
from hug.format import parse_content_type, content_type, underscore, camelcase
from hug import _empty as empty

@pytest.fixture
def sample_text():
    return "sampleText"

@pytest.fixture
def sample_text_underscore():
    return "sample_text"

@pytest.fixture
def sample_content_type_with_params():
    return "text/html; charset=UTF-8"

@pytest.fixture
def sample_content_type_without_params():
    return "text/html"

def test_parse_content_type_with_params(sample_content_type_with_params):
    content_type, params = parse_content_type(sample_content_type_with_params)
    assert content_type == "text/html"
    assert params == {"charset": "UTF-8"}

def test_parse_content_type_without_params(sample_content_type_without_params):
    content_type, params = parse_content_type(sample_content_type_without_params)
    assert content_type == "text/html"
    assert params == empty.dict

def test_content_type_decorator():
    @content_type("application/json")
    def sample_function():
        pass

    assert sample_function.content_type == "application/json"

def test_underscore(sample_text):
    assert underscore(sample_text) == "sample_text"

def test_camelcase(sample_text_underscore):
    assert camelcase(sample_text_underscore) == "sampleText"