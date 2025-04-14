import pytest
from unittest.mock import Mock
from hug.middleware import SessionMiddleware, LogMiddleware, CORSMiddleware

@pytest.fixture
def mock_store():
    store = Mock()
    store.exists.return_value = False
    store.get.return_value = {}
    return store

@pytest.fixture
def mock_request():
    request = Mock()
    request.cookies = {}
    request.context = {}
    request.remote_addr = '127.0.0.1'
    request.method = 'GET'
    request.relative_uri = '/test'
    request.content_type = 'application/json'
    request.user_agent = 'pytest'
    request.path = '/test'
    request.get_header = Mock(return_value=None)
    return request

@pytest.fixture
def mock_response():
    response = Mock()
    response.data = None
    response.status = '200 OK'
    response.set_cookie = Mock()
    response.set_header = Mock()
    return response

@pytest.fixture
def mock_api():
    api = Mock()
    api.http.routes = {
        '/test': {
            'GET': {},
            'POST': {},
        }
    }
    api.http.base_url = ''
    return api

def test_session_middleware_process_request(mock_store, mock_request, mock_response):
    middleware = SessionMiddleware(store=mock_store)
    middleware.process_request(mock_request, mock_response)
    assert mock_request.context['session'] == {}

def test_session_middleware_process_response(mock_store, mock_request, mock_response):
    middleware = SessionMiddleware(store=mock_store)
    middleware.process_response(mock_request, mock_response, None, True)
    assert mock_store.set.called

def test_log_middleware_process_request(mock_request, mock_response, caplog):
    middleware = LogMiddleware()
    middleware.process_request(mock_request, mock_response)
    assert "Requested: GET /test application/json" in caplog.text

def test_log_middleware_process_response(mock_request, mock_response, caplog):
    middleware = LogMiddleware()
    middleware.process_response(mock_request, mock_response, None, True)
    assert "127.0.0.1 - - [2025-04-11 18:55:23]" in caplog.text

def test_cors_middleware_process_response(mock_api, mock_request, mock_response):
    middleware = CORSMiddleware(api=mock_api)
    middleware.process_response(mock_request, mock_response, None, True)
    assert mock_response.set_header.called

def test_cors_middleware_options_request(mock_api, mock_request, mock_response):
    mock_request.method = 'OPTIONS'
    middleware = CORSMiddleware(api=mock_api)
    middleware.process_response(mock_request, mock_response, None, True)
    mock_response.set_header.assert_any_call("Access-Control-Allow-Methods", "OPTIONS, GET, POST")
    mock_response.set_header.assert_any_call("Allow", "OPTIONS, GET, POST")