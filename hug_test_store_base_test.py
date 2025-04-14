import pytest
from hug.store import InMemoryStore
from hug.exceptions import StoreKeyNotFound

def test_set_and_get():
    store = InMemoryStore()
    store.set("key1", "value1")
    assert store.get("key1") == "value1"

def test_get_nonexistent_key():
    store = InMemoryStore()
    with pytest.raises(StoreKeyNotFound):
        store.get("nonexistent_key")

def test_exists():
    store = InMemoryStore()
    assert not store.exists("key1")
    store.set("key1", "value1")
    assert store.exists("key1")

def test_delete():
    store = InMemoryStore()
    store.set("key1", "value1")
    assert store.exists("key1")
    store.delete("key1")
    assert not store.exists("key1")

def test_delete_nonexistent_key():
    store = InMemoryStore()
    store.delete("nonexistent_key")  # Should not raise any exception