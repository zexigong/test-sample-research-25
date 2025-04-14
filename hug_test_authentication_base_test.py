import base64
import pytest
from falcon import HTTPUnauthorized
from hug.authentication import basic, api_key, token, verify

class MockRequest:
    def __init__(self, auth=None, headers=None):
        self.auth = auth
        self.headers = headers or {}

    def get_header(self, name):
        return self.headers.get(name, None)

class MockResponse:
    def __init__(self):
        self.headers = {}

    def set_header(self, name, value):
        self.headers[name] = value

def test_basic_auth_success():
    request = MockRequest(auth='Basic ' + base64.b64encode(b'user:password').decode('utf-8'))
    response = MockResponse()
    verify_user = verify('user', 'password')
    assert basic(request, response, verify_user) == 'user'
    assert response.headers['WWW-Authenticate'] == ''

def test_basic_auth_no_auth():
    request = MockRequest(auth=None)
    response = MockResponse()
    verify_user = verify('user', 'password')
    with pytest.raises(HTTPUnauthorized):
        basic(request, response, verify_user)

def test_basic_auth_invalid_auth_type():
    request = MockRequest(auth='Bearer token')
    response = MockResponse()
    verify_user = verify('user', 'password')
    with pytest.raises(HTTPUnauthorized):
        basic(request, response, verify_user)

def test_basic_auth_improperly_formed():
    request = MockRequest(auth='Basic')
    response = MockResponse()
    verify_user = verify('user', 'password')
    with pytest.raises(HTTPUnauthorized):
        basic(request, response, verify_user)

def test_basic_auth_invalid_credentials():
    request = MockRequest(auth='Basic ' + base64.b64encode(b'user:wrongpassword').decode('utf-8'))
    response = MockResponse()
    verify_user = verify('user', 'password')
    with pytest.raises(HTTPUnauthorized):
        basic(request, response, verify_user)

def test_api_key_auth_success():
    request = MockRequest(headers={'X-Api-Key': 'valid_api_key'})
    response = MockResponse()
    verify_user = lambda api_key: 'user' if api_key == 'valid_api_key' else False
    assert api_key(request, response, verify_user) == 'user'

def test_api_key_auth_no_key():
    request = MockRequest(headers={})
    response = MockResponse()
    verify_user = lambda api_key: 'user' if api_key == 'valid_api_key' else False
    with pytest.raises(HTTPUnauthorized):
        api_key(request, response, verify_user)

def test_api_key_auth_invalid_key():
    request = MockRequest(headers={'X-Api-Key': 'invalid_api_key'})
    response = MockResponse()
    verify_user = lambda api_key: 'user' if api_key == 'valid_api_key' else False
    with pytest.raises(HTTPUnauthorized):
        api_key(request, response, verify_user)

def test_token_auth_success():
    request = MockRequest(headers={'Authorization': 'valid_token'})
    response = MockResponse()
    verify_user = lambda token: 'user' if token == 'valid_token' else False
    assert token(request, response, verify_user) == 'user'

def test_token_auth_no_token():
    request = MockRequest(headers={})
    response = MockResponse()
    verify_user = lambda token: 'user' if token == 'valid_token' else False
    with pytest.raises(HTTPUnauthorized):
        token(request, response, verify_user)

def test_token_auth_invalid_token():
    request = MockRequest(headers={'Authorization': 'invalid_token'})
    response = MockResponse()
    verify_user = lambda token: 'user' if token == 'valid_token' else False
    with pytest.raises(HTTPUnauthorized):
        token(request, response, verify_user)