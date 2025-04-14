import pytest
from unittest.mock import Mock
from hug.transform import content_type, suffix, prefix, all

@pytest.fixture
def mock_request():
    return Mock()

def test_content_type_transformer_found(mock_request):
    mock_request.content_type = 'application/json'
    transformers = {'application/json': lambda data: {'transformed': data}}
    transform = content_type(transformers)
    result = transform('data', mock_request)
    assert result == {'transformed': 'data'}

def test_content_type_transformer_not_found(mock_request):
    mock_request.content_type = 'application/xml'
    transformers = {'application/json': lambda data: {'transformed': data}}
    transform = content_type(transformers)
    result = transform('data', mock_request)
    assert result == 'data'

def test_content_type_default_transformer(mock_request):
    mock_request.content_type = 'application/xml'
    transformers = {'application/json': lambda data: {'transformed': data}}
    default_transformer = lambda data: {'default_transformed': data}
    transform = content_type(transformers, default=default_transformer)
    result = transform('data', mock_request)
    assert result == {'default_transformed': 'data'}

def test_suffix_transformer_found(mock_request):
    mock_request.path = '/test.json'
    transformers = {'.json': lambda data: {'transformed': data}}
    transform = suffix(transformers)
    result = transform('data', mock_request)
    assert result == {'transformed': 'data'}

def test_suffix_transformer_not_found(mock_request):
    mock_request.path = '/test.xml'
    transformers = {'.json': lambda data: {'transformed': data}}
    transform = suffix(transformers)
    result = transform('data', mock_request)
    assert result == 'data'

def test_suffix_default_transformer(mock_request):
    mock_request.path = '/test.xml'
    transformers = {'.json': lambda data: {'transformed': data}}
    default_transformer = lambda data: {'default_transformed': data}
    transform = suffix(transformers, default=default_transformer)
    result = transform('data', mock_request)
    assert result == {'default_transformed': 'data'}

def test_prefix_transformer_found(mock_request):
    mock_request.path = '/api/test'
    transformers = {'/api': lambda data: {'transformed': data}}
    transform = prefix(transformers)
    result = transform('data', mock_request)
    assert result == {'transformed': 'data'}

def test_prefix_transformer_not_found(mock_request):
    mock_request.path = '/web/test'
    transformers = {'/api': lambda data: {'transformed': data}}
    transform = prefix(transformers)
    result = transform('data', mock_request)
    assert result == 'data'

def test_prefix_default_transformer(mock_request):
    mock_request.path = '/web/test'
    transformers = {'/api': lambda data: {'transformed': data}}
    default_transformer = lambda data: {'default_transformed': data}
    transform = prefix(transformers, default=default_transformer)
    result = transform('data', mock_request)
    assert result == {'default_transformed': 'data'}

def test_all_transformers():
    transformer_1 = lambda data, **kwargs: data + '_transformed_1'
    transformer_2 = lambda data, **kwargs: data + '_transformed_2'
    transform = all(transformer_1, transformer_2)
    result = transform('data')
    assert result == 'data_transformed_1_transformed_2'