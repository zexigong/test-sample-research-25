import hug
import pytest

from hug.middleware import CORSMiddleware, LogMiddleware, SessionMiddleware

try:
    import falcon  # type: ignore
except ImportError:
    falcon = None  # type: ignore


class FakeStore:
    def __init__(self):
        self.store = {}

    def exists(self, session_id):
        return session_id in self.store

    def get(self, session_id):
        return self.store[session_id]

    def set(self, session_id, data):
        self.store[session_id] = data


@pytest.mark.skipif(falcon is None, reason="requires falcon framework")
def test_session_middleware():
    """Test to ensure that the session middleware works as expected"""
    store = FakeStore()
    session_middleware = SessionMiddleware(store)

    @hug.get()
    def store_value(request, response, name: str):
        request.context["session"]["name"] = name
        return f"Hello, {name}!"

    @hug.get()
    def show_value(request, response):
        return f"Hello, {request.context['session']['name']}!"

    api = hug.API(__name__)
    api.http.add_middleware(session_middleware)
    api.http.add_sink(store_value, ["store"])
    api.http.add_sink(show_value, ["show"])

    store_value_url = hug.test.get(api, "store", name="Timothy")
    show_value_url = hug.test.get(api, "show", cookies=store_value_url.cookies)
    assert show_value_url.data == b"Hello, Timothy!"


@pytest.mark.skipif(falcon is None, reason="requires falcon framework")
def test_log_middleware():
    """Test to ensure that the log middleware works as expected"""

    class FakeLogger:
        def __init__(self):
            self.logged = []

        def info(self, message):
            self.logged.append(message)

    fake_logger = FakeLogger()
    log_middleware = LogMiddleware(fake_logger)

    @hug.get()
    def say_hello():
        return "Hello!"

    api = hug.API(__name__)
    api.http.add_middleware(log_middleware)
    api.http.add_sink(say_hello, ["say_hello"])

    assert hug.test.get(api, "say_hello").data == b"Hello!"
    assert fake_logger.logged


@pytest.mark.skipif(falcon is None, reason="requires falcon framework")
def test_cors_middleware():
    """Test to ensure that the cors middleware works as expected"""

    @hug.get()
    def say_hello():
        return "Hello!"

    @hug.get("/v2/say_hello")
    def say_hello_v2():
        return "Hello!"

    api = hug.API(__name__)
    api.http.add_middleware(CORSMiddleware(api))
    api.http.add_sink(say_hello, ["say_hello"])
    api.http.add_sink(say_hello_v2, ["v2/say_hello"])

    assert hug.test.get(api, "say_hello").data == b"Hello!"
    assert hug.test.get(api, "v2/say_hello").data == b"Hello!"