import pytest

import hug
from hug.store import InMemoryStore


def test_store_get():
    store = InMemoryStore()
    store._data["test"] = "value"
    assert store.get("test") == "value"


def test_store_get_exception():
    store = InMemoryStore()
    with pytest.raises(hug.exceptions.StoreKeyNotFound):
        store.get("test")


def test_store_exists():
    store = InMemoryStore()
    store._data["test"] = "value"
    assert store.exists("test")


def test_store_exists_not():
    store = InMemoryStore()
    assert not store.exists("test")


def test_store_set():
    store = InMemoryStore()
    store.set("test", "value")
    assert store._data["test"] == "value"


def test_store_delete():
    store = InMemoryStore()
    store._data["test"] = "value"
    store.delete("test")
    assert "test" not in store._data


def test_store_delete_not():
    store = InMemoryStore()
    store.delete("test")