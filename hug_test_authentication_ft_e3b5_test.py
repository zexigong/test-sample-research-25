import base64
from unittest.mock import Mock

import falcon
import pytest

import hug
import hug.authentication


def test_basic_authentication():
    """Test to ensure that basic authentication works as expected"""
    hug_api = hug.API("fake_authentication")

    @hug.get(requires=hug.authentication.basic(hug.authentication.verify("timothy", "deadbeef")), api=hug_api)
    def basic_auth_call():
        return True

    basic_auth_call.interface.http(requires=None)(**{"hug.API": hug_api})

    with pytest.raises(falcon.HTTPUnauthorized):
        hug.test.get(hug_api, "basic_auth_call")

    with pytest.raises(falcon.HTTPUnauthorized):
        hug.test.get(hug_api, "basic_auth_call", headers={"Authorization": "Basic NotGonnaWork"})

    with pytest.raises(falcon.HTTPUnauthorized):
        hug.test.get(
            hug_api,
            "basic_auth_call",
            headers={"Authorization": "Basic {0}".format(base64.b64encode(b"timothy:deadbeef").decode("utf8"))},
        )

    assert (
        hug.test.get(
            hug_api,
            "basic_auth_call",
            headers={"Authorization": "Basic {0}".format(base64.b64encode(b"timothy:deadbeef").decode("utf8"))},
        ).data
        is True
    )


def test_basic_authentication_non_string():
    """Test to ensure that basic authentication works as expected when given a non-string authorization header"""
    hug_api = hug.API("fake_authentication")

    @hug.get(requires=hug.authentication.basic(hug.authentication.verify("timothy", "deadbeef")), api=hug_api)
    def basic_auth_call():
        return True

    basic_auth_call.interface.http(requires=None)(**{"hug.API": hug_api})

    auth = Mock()
    auth.auth = base64.b64encode(b"timothy:deadbeef")
    assert basic_auth_call(auth=auth)


def test_basic_authentication_invalid_header():
    """Test to ensure that basic authentication raises an error when provided with an invalid header"""
    hug_api = hug.API("fake_authentication")

    @hug.get(requires=hug.authentication.basic(hug.authentication.verify("timothy", "deadbeef")), api=hug_api)
    def basic_auth_call():
        return True

    with pytest.raises(falcon.HTTPUnauthorized):
        basic_auth_call(auth="invalid")


def test_basic_authentication_invalid_credentials():
    """Test to ensure that basic authentication raises an error when provided with invalid credentials"""
    hug_api = hug.API("fake_authentication")

    @hug.get(requires=hug.authentication.basic(hug.authentication.verify("timothy", "deadbeef")), api=hug_api)
    def basic_auth_call():
        return True

    auth = Mock()
    auth.auth = base64.b64encode(b"timothy")
    with pytest.raises(falcon.HTTPUnauthorized):
        basic_auth_call(auth=auth)


def test_basic_authentication_invalid_encoding():
    """Test to ensure that basic authentication raises an error when provided with invalid encoding"""
    hug_api = hug.API("fake_authentication")

    @hug.get(requires=hug.authentication.basic(hug.authentication.verify("timothy", "deadbeef")), api=hug_api)
    def basic_auth_call():
        return True

    auth = Mock()
    auth.auth = "Basic invalid"
    with pytest.raises(falcon.HTTPUnauthorized):
        basic_auth_call(auth=auth)


def test_basic_authentication_context():
    """Test to ensure that basic authentication works with a context parameter"""
    hug_api = hug.API("fake_authentication")

    def verify(username, password, context):
        if context.get("secret") == "hush" and username == "timothy" and password == "deadbeef":
            return username
        return False

    @hug.get(requires=hug.authentication.basic(verify), api=hug_api)
    def basic_auth_call():
        return True

    auth = Mock()
    auth.auth = base64.b64encode(b"timothy:deadbeef")
    assert basic_auth_call(auth=auth, context={"secret": "hush"})


def test_token_authentication():
    """Test to ensure that token authentication works as expected"""
    hug_api = hug.API("fake_authentication")

    @hug.get(requires=hug.authentication.token(lambda token: token == "deadbeef"), api=hug_api)
    def token_auth_call():
        return True

    token_auth_call.interface.http(requires=None)(**{"hug.API": hug_api})

    with pytest.raises(falcon.HTTPUnauthorized):
        hug.test.get(hug_api, "token_auth_call")

    with pytest.raises(falcon.HTTPUnauthorized):
        hug.test.get(hug_api, "token_auth_call", headers={"Authorization": "deadbeef2"})

    assert hug.test.get(hug_api, "token_auth_call", headers={"Authorization": "deadbeef"}).data is True


def test_token_authentication_context():
    """Test to ensure that token authentication works with a context parameter"""
    hug_api = hug.API("fake_authentication")

    def verify(token, context):
        if context.get("secret") == "hush" and token == "deadbeef":
            return True
        return False

    @hug.get(requires=hug.authentication.token(verify), api=hug_api)
    def token_auth_call():
        return True

    assert token_auth_call(Authorization="deadbeef", context={"secret": "hush"})


def test_api_key_authentication():
    """Test to ensure that API key authentication works as expected"""
    hug_api = hug.API("fake_authentication")

    @hug.get(requires=hug.authentication.api_key(lambda key: key == "deadbeef"), api=hug_api)
    def api_key_auth_call():
        return True

    api_key_auth_call.interface.http(requires=None)(**{"hug.API": hug_api})

    with pytest.raises(falcon.HTTPUnauthorized):
        hug.test.get(hug_api, "api_key_auth_call")

    with pytest.raises(falcon.HTTPUnauthorized):
        hug.test.get(hug_api, "api_key_auth_call", headers={"X-Api-Key": "deadbeef2"})

    assert hug.test.get(hug_api, "api_key_auth_call", headers={"X-Api-Key": "deadbeef"}).data is True


def test_api_key_authentication_context():
    """Test to ensure that API key authentication works with a context parameter"""
    hug_api = hug.API("fake_authentication")

    def verify(token, context):
        if context.get("secret") == "hush" and token == "deadbeef":
            return True
        return False

    @hug.get(requires=hug.authentication.api_key(verify), api=hug_api)
    def api_key_auth_call():
        return True

    assert api_key_auth_call(**{"X-Api-Key": "deadbeef"}, context={"secret": "hush"})