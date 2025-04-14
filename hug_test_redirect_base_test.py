import pytest
import falcon
from hug.redirect import to, permanent, found, see_other, temporary, not_found

def test_to_redirect():
    with pytest.raises(falcon.http_status.HTTPStatus) as excinfo:
        to("http://example.com")
    assert excinfo.value.status == falcon.HTTP_302
    assert excinfo.value.headers["location"] == "http://example.com"

def test_permanent_redirect():
    with pytest.raises(falcon.http_status.HTTPStatus) as excinfo:
        permanent("http://example.com")
    assert excinfo.value.status == falcon.HTTP_301
    assert excinfo.value.headers["location"] == "http://example.com"

def test_found_redirect():
    with pytest.raises(falcon.http_status.HTTPStatus) as excinfo:
        found("http://example.com")
    assert excinfo.value.status == falcon.HTTP_302
    assert excinfo.value.headers["location"] == "http://example.com"

def test_see_other_redirect():
    with pytest.raises(falcon.http_status.HTTPStatus) as excinfo:
        see_other("http://example.com")
    assert excinfo.value.status == falcon.HTTP_303
    assert excinfo.value.headers["location"] == "http://example.com"

def test_temporary_redirect():
    with pytest.raises(falcon.http_status.HTTPStatus) as excinfo:
        temporary("http://example.com")
    assert excinfo.value.status == falcon.HTTP_307
    assert excinfo.value.headers["location"] == "http://example.com"

def test_not_found():
    with pytest.raises(falcon.HTTPNotFound):
        not_found()