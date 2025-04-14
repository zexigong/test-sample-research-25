import pytest
from hug.exceptions import InvalidTypeData, StoreKeyNotFound, SessionNotFound

def test_invalid_type_data_exception():
    message = "Invalid data type"
    reasons = {"expected": "int", "received": "str"}
    exception = InvalidTypeData(message, reasons)
    
    assert exception.message == message
    assert exception.reasons == reasons

def test_store_key_not_found_exception():
    with pytest.raises(StoreKeyNotFound):
        raise StoreKeyNotFound("Store key not found")

def test_session_not_found_exception():
    with pytest.raises(SessionNotFound):
        raise SessionNotFound("Session ID not found")