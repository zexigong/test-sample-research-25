import pytest
import falcon

import hug.redirect


def test_redirect_temporary():
    with pytest.raises(falcon.http_status.HTTPStatus) as redirect:
        hug.redirect.temporary("https://google.com")

    assert redirect.value.status == falcon.HTTP_307
    assert redirect.value.headers["location"] == "https://google.com"


def test_redirect_found():
    with pytest.raises(falcon.http_status.HTTPStatus) as redirect:
        hug.redirect.found("https://google.com")

    assert redirect.value.status == falcon.HTTP_302
    assert redirect.value.headers["location"] == "https://google.com"


def test_redirect_see_other():
    with pytest.raises(falcon.http_status.HTTPStatus) as redirect:
        hug.redirect.see_other("https://google.com")

    assert redirect.value.status == falcon.HTTP_303
    assert redirect.value.headers["location"] == "https://google.com"


def test_redirect_permanent():
    with pytest.raises(falcon.http_status.HTTPStatus) as redirect:
        hug.redirect.permanent("https://google.com")

    assert redirect.value.status == falcon.HTTP_301
    assert redirect.value.headers["location"] == "https://google.com"


def test_redirect_to():
    with pytest.raises(falcon.http_status.HTTPStatus) as redirect:
        hug.redirect.to("https://google.com", falcon.HTTP_308)

    assert redirect.value.status == falcon.HTTP_308
    assert redirect.value.headers["location"] == "https://google.com"


def test_redirect_not_found():
    with pytest.raises(falcon.HTTPNotFound):
        hug.redirect.not_found()