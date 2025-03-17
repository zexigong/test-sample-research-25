import pytest
from twisted.protocols.memcache import MemCacheProtocol, Command, NoSuchCommand, ClientError, ServerError
from twisted.internet.defer import Deferred, TimeoutError, fail
from twisted.test.proto_helpers import MemoryReactor
from collections import deque

@pytest.fixture
def protocol():
    reactor = MemoryReactor()
    return MemCacheProtocol()

def test_connection_timeout(protocol):
    protocol.transport = MemoryReactor()
    protocol.timeoutConnection()
    assert protocol._disconnected

def test_connection_lost(protocol):
    reason = Exception("Lost connection")
    protocol.transport = MemoryReactor()
    protocol.connectionLost(reason)
    assert protocol._disconnected

def test_send_line(protocol):
    protocol.transport = MemoryReactor()
    protocol.sendLine(b"test")
    assert protocol.transport.value() == b"test\r\n"

def test_raw_data_received(protocol):
    protocol._lenExpected = 4
    protocol._getBuffer = []
    protocol._bufferLength = 0
    protocol._current.append(Command(b"get", key=b"mykey", multiple=False))
    protocol.rawDataReceived(b"data\r\n")
    assert protocol._current[0].value == b"data"

def test_cmd_stored(protocol):
    protocol._current.append(Command(b"set", key=b"mykey"))
    protocol.cmd_STORED()
    assert protocol._current[0]._deferred.called

def test_cmd_not_stored(protocol):
    protocol._current.append(Command(b"set", key=b"mykey"))
    protocol.cmd_NOT_STORED()
    assert not protocol._current[0]._deferred.called

def test_cmd_end(protocol):
    protocol._current.append(Command(b"get", key=b"mykey", multiple=False))
    protocol.cmd_END()
    assert protocol._current[0]._deferred.called

def test_cmd_not_found(protocol):
    protocol._current.append(Command(b"delete", key=b"mykey"))
    protocol.cmd_NOT_FOUND()
    assert not protocol._current[0]._deferred.called

def test_cmd_value(protocol):
    protocol._current.append(Command(b"get", key=b"mykey", multiple=False))
    protocol.cmd_VALUE(b"mykey 0 4")
    assert protocol._lenExpected == 4

def test_cmd_stat(protocol):
    protocol._current.append(Command(b"stats", values={}))
    protocol.cmd_STAT(b"mykey value")
    assert protocol._current[0].values[b"mykey"] == b"value"

def test_cmd_version(protocol):
    protocol._current.append(Command(b"version"))
    protocol.cmd_VERSION(b"1.0.0")
    assert protocol._current[0]._deferred.called

def test_cmd_error(protocol):
    protocol._current.append(Command(b"invalid"))
    protocol.cmd_ERROR()
    assert isinstance(protocol._current[0]._deferred.result, NoSuchCommand)

def test_cmd_client_error(protocol):
    protocol._current.append(Command(b"invalid"))
    protocol.cmd_CLIENT_ERROR(b"invalid input")
    assert isinstance(protocol._current[0]._deferred.result, ClientError)

def test_cmd_server_error(protocol):
    protocol._current.append(Command(b"invalid"))
    protocol.cmd_SERVER_ERROR(b"server error")
    assert isinstance(protocol._current[0]._deferred.result, ServerError)

def test_cmd_deleted(protocol):
    protocol._current.append(Command(b"delete", key=b"mykey"))
    protocol.cmd_DELETED()
    assert protocol._current[0]._deferred.called

def test_cmd_ok(protocol):
    protocol._current.append(Command(b"flush_all"))
    protocol.cmd_OK()
    assert protocol._current[0]._deferred.called

def test_cmd_exists(protocol):
    protocol._current.append(Command(b"cas", key=b"mykey"))
    protocol.cmd_EXISTS()
    assert not protocol._current[0]._deferred.called

def test_line_received(protocol):
    protocol.transport = MemoryReactor()
    protocol.lineReceived(b"STORED")
    assert protocol._current[0]._deferred.called

def test_increment(protocol):
    protocol.transport = MemoryReactor()
    d = protocol.increment(b"mykey", 1)
    assert isinstance(d, Deferred)

def test_decrement(protocol):
    protocol.transport = MemoryReactor()
    d = protocol.decrement(b"mykey", 1)
    assert isinstance(d, Deferred)

def test_replace(protocol):
    protocol.transport = MemoryReactor()
    d = protocol.replace(b"mykey", b"value")
    assert isinstance(d, Deferred)

def test_add(protocol):
    protocol.transport = MemoryReactor()
    d = protocol.add(b"mykey", b"value")
    assert isinstance(d, Deferred)

def test_set(protocol):
    protocol.transport = MemoryReactor()
    d = protocol.set(b"mykey", b"value")
    assert isinstance(d, Deferred)

def test_check_and_set(protocol):
    protocol.transport = MemoryReactor()
    d = protocol.checkAndSet(b"mykey", b"value", b"cas")
    assert isinstance(d, Deferred)

def test_append(protocol):
    protocol.transport = MemoryReactor()
    d = protocol.append(b"mykey", b"value")
    assert isinstance(d, Deferred)

def test_prepend(protocol):
    protocol.transport = MemoryReactor()
    d = protocol.prepend(b"mykey", b"value")
    assert isinstance(d, Deferred)

def test_get(protocol):
    protocol.transport = MemoryReactor()
    d = protocol.get(b"mykey")
    assert isinstance(d, Deferred)

def test_get_multiple(protocol):
    protocol.transport = MemoryReactor()
    d = protocol.getMultiple([b"mykey1", b"mykey2"])
    assert isinstance(d, Deferred)

def test_stats(protocol):
    protocol.transport = MemoryReactor()
    d = protocol.stats()
    assert isinstance(d, Deferred)

def test_version(protocol):
    protocol.transport = MemoryReactor()
    d = protocol.version()
    assert isinstance(d, Deferred)

def test_delete(protocol):
    protocol.transport = MemoryReactor()
    d = protocol.delete(b"mykey")
    assert isinstance(d, Deferred)

def test_flush_all(protocol):
    protocol.transport = MemoryReactor()
    d = protocol.flushAll()
    assert isinstance(d, Deferred)