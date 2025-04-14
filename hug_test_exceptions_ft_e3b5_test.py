import pytest

import hug.exceptions as exceptions


def test_InvalidTypeData():
    assert exceptions.InvalidTypeData("Test").message == "Test"
    assert exceptions.InvalidTypeData("Test").reasons is None
    assert exceptions.InvalidTypeData("Test", reasons="Test2").reasons == "Test2"


def test_StoreKeyNotFound():
    assert exceptions.StoreKeyNotFound("Test").args[0] == "Test"


def test_SessionNotFound():
    assert exceptions.SessionNotFound("Test").args[0] == "Test"