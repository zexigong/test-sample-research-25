# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

"""
Tests for twisted.protocols.memcache.
"""

from collections import defaultdict

from twisted.internet.defer import CancelledError, Deferred, TimeoutError, fail, succeed
from twisted.internet.error import ConnectionDone, ConnectionLost
from twisted.internet.protocol import ClientFactory
from twisted.python.failure import Failure
from twisted.trial import unittest
from twisted.protocols.memcache import (
    ClientError,
    MemCacheProtocol,
    ServerError,
)


class MemCacheTestCase(unittest.TestCase):
    """
    Tests for L{MemCacheProtocol}.
    """

    def setUp(self):
        """
        Initialize the protocol and mock transport.
        """
        self.proto = MemCacheProtocol()
        self.tr = FakeTransport()
        self.proto.makeConnection(self.tr)

    def tearDown(self):
        """
        Disconnect the protocol.
        """
        self.proto.connectionLost(Failure(ConnectionDone()))

    def test_set(self):
        """
        Test L{MemCacheProtocol.set}.
        """
        d = self.proto.set(b"foo", b"bar")
        self.assertEqual(self.tr.value(), b"set foo 0 0 3\r\nbar\r\n")
        self.proto.dataReceived(b"STORED\r\n")
        self.assertEqual(self.successResultOf(d), True)

    def test_setTimeout(self):
        """
        Test L{MemCacheProtocol.set} timeout.
        """
        self.proto.timeOut = 0.1
        d = self.proto.set(b"foo", b"bar")
        self.assertEqual(self.tr.value(), b"set foo 0 0 3\r\nbar\r\n")
        self.assertFalse(d.called)
        self.assertFailure(d, TimeoutError)
        self.assertEqual(self.tr.disconnectReason.type, TimeoutError)

    def test_setKeyTooLong(self):
        """
        Test L{MemCacheProtocol.set} with a key that is too long.
        """
        self.assertFailure(self.proto.set(b"x" * 251, b"bar"), ClientError)

    def test_setKeyWrongType(self):
        """
        Test L{MemCacheProtocol.set} with a key that is the wrong type.
        """
        self.assertFailure(self.proto.set(1, b"bar"), ClientError)

    def test_setValueWrongType(self):
        """
        Test L{MemCacheProtocol.set} with a value that is the wrong type.
        """
        self.assertFailure(self.proto.set(b"foo", 1), ClientError)

    def test_setNoConnection(self):
        """
        Test L{MemCacheProtocol.set} with no connection.
        """
        self.proto.transport.loseConnection()
        d = self.proto.set(b"foo", b"bar")
        self.assertEqual(self.tr.value(), b"set foo 0 0 3\r\nbar\r\n")
        self.assertFailure(d, RuntimeError)

    def test_setClientError(self):
        """
        Test L{MemCacheProtocol.set} with a client error.
        """
        d = self.proto.set(b"foo", b"bar")
        self.assertEqual(self.tr.value(), b"set foo 0 0 3\r\nbar\r\n")
        self.proto.dataReceived(b"CLIENT_ERROR test\r\n")
        self.assertFailure(d, ClientError)

    def test_setServerError(self):
        """
        Test L{MemCacheProtocol.set} with a server error.
        """
        d = self.proto.set(b"foo", b"bar")
        self.assertEqual(self.tr.value(), b"set foo 0 0 3\r\nbar\r\n")
        self.proto.dataReceived(b"SERVER_ERROR test\r\n")
        self.assertFailure(d, ServerError)

    def test_get(self):
        """
        Test L{MemCacheProtocol.get}.
        """
        d = self.proto.get(b"foo")
        self.assertEqual(self.tr.value(), b"get foo\r\n")
        self.proto.dataReceived(b"VALUE foo 0 3\r\nbar\r\nEND\r\n")
        self.assertEqual(self.successResultOf(d), (0, b"bar"))

    def test_getTimeout(self):
        """
        Test L{MemCacheProtocol.get} timeout.
        """
        self.proto.timeOut = 0.1
        d = self.proto.get(b"foo")
        self.assertEqual(self.tr.value(), b"get foo\r\n")
        self.assertFalse(d.called)
        self.assertFailure(d, TimeoutError)
        self.assertEqual(self.tr.disconnectReason.type, TimeoutError)

    def test_getKeyTooLong(self):
        """
        Test L{MemCacheProtocol.get} with a key that is too long.
        """
        self.assertFailure(self.proto.get(b"x" * 251), ClientError)

    def test_getKeyWrongType(self):
        """
        Test L{MemCacheProtocol.get} with a key that is the wrong type.
        """
        self.assertFailure(self.proto.get(1), ClientError)

    def test_getNoConnection(self):
        """
        Test L{MemCacheProtocol.get} with no connection.
        """
        self.proto.transport.loseConnection()
        d = self.proto.get(b"foo")
        self.assertEqual(self.tr.value(), b"get foo\r\n")
        self.assertFailure(d, RuntimeError)

    def test_getNotFound(self):
        """
        Test L{MemCacheProtocol.get} with a key that is not found.
        """
        d = self.proto.get(b"foo")
        self.assertEqual(self.tr.value(), b"get foo\r\n")
        self.proto.dataReceived(b"END\r\n")
        self.assertEqual(self.successResultOf(d), (0, None))

    def test_getClientError(self):
        """
        Test L{MemCacheProtocol.get} with a client error.
        """
        d = self.proto.get(b"foo")
        self.assertEqual(self.tr.value(), b"get foo\r\n")
        self.proto.dataReceived(b"CLIENT_ERROR test\r\n")
        self.assertFailure(d, ClientError)

    def test_getServerError(self):
        """
        Test L{MemCacheProtocol.get} with a server error.
        """
        d = self.proto.get(b"foo")
        self.assertEqual(self.tr.value(), b"get foo\r\n")
        self.proto.dataReceived(b"SERVER_ERROR test\r\n")
        self.assertFailure(d, ServerError)

    def test_gets(self):
        """
        Test L{MemCacheProtocol.get} with an identifier.
        """
        d = self.proto.get(b"foo", withIdentifier=True)
        self.assertEqual(self.tr.value(), b"gets foo\r\n")
        self.proto.dataReceived(b"VALUE foo 0 3 12345\r\nbar\r\nEND\r\n")
        self.assertEqual(self.successResultOf(d), (0, b"12345", b"bar"))

    def test_getMultiple(self):
        """
        Test L{MemCacheProtocol.getMultiple}.
        """
        d = self.proto.getMultiple([b"foo", b"bar"])
        self.assertEqual(self.tr.value(), b"get foo bar\r\n")
        self.proto.dataReceived(
            b"VALUE foo 0 3\r\nval\r\nVALUE bar 1 4\r\nue2\r\nEND\r\n"
        )
        self.assertEqual(
            self.successResultOf(d), {b"foo": (0, b"val"), b"bar": (1, b"ue2")}
        )

    def test_getMultipleTimeout(self):
        """
        Test L{MemCacheProtocol.getMultiple} timeout.
        """
        self.proto.timeOut = 0.1
        d = self.proto.getMultiple([b"foo", b"bar"])
        self.assertEqual(self.tr.value(), b"get foo bar\r\n")
        self.assertFalse(d.called)
        self.assertFailure(d, TimeoutError)
        self.assertEqual(self.tr.disconnectReason.type, TimeoutError)

    def test_getMultipleKeyTooLong(self):
        """
        Test L{MemCacheProtocol.getMultiple} with a key that is too long.
        """
        self.assertFailure(self.proto.getMultiple([b"x" * 251]), ClientError)

    def test_getMultipleKeyWrongType(self):
        """
        Test L{MemCacheProtocol.getMultiple} with a key that is the wrong type.
        """
        self.assertFailure(self.proto.getMultiple([1]), ClientError)

    def test_getMultipleNoConnection(self):
        """
        Test L{MemCacheProtocol.getMultiple} with no connection.
        """
        self.proto.transport.loseConnection()
        d = self.proto.getMultiple([b"foo", b"bar"])
        self.assertEqual(self.tr.value(), b"get foo bar\r\n")
        self.assertFailure(d, RuntimeError)

    def test_getMultipleNotFound(self):
        """
        Test L{MemCacheProtocol.getMultiple} with a key that is not found.
        """
        d = self.proto.getMultiple([b"foo", b"bar"])
        self.assertEqual(self.tr.value(), b"get foo bar\r\n")
        self.proto.dataReceived(b"END\r\n")
        self.assertEqual(
            self.successResultOf(d), {b"foo": (0, None), b"bar": (0, None)}
        )

    def test_getMultipleClientError(self):
        """
        Test L{MemCacheProtocol.getMultiple} with a client error.
        """
        d = self.proto.getMultiple([b"foo", b"bar"])
        self.assertEqual(self.tr.value(), b"get foo bar\r\n")
        self.proto.dataReceived(b"CLIENT_ERROR test\r\n")
        self.assertFailure(d, ClientError)

    def test_getMultipleServerError(self):
        """
        Test L{MemCacheProtocol.getMultiple} with a server error.
        """
        d = self.proto.getMultiple([b"foo", b"bar"])
        self.assertEqual(self.tr.value(), b"get foo bar\r\n")
        self.proto.dataReceived(b"SERVER_ERROR test\r\n")
        self.assertFailure(d, ServerError)

    def test_getsMultiple(self):
        """
        Test L{MemCacheProtocol.getMultiple} with an identifier.
        """
        d = self.proto.getMultiple([b"foo", b"bar"], withIdentifier=True)
        self.assertEqual(self.tr.value(), b"gets foo bar\r\n")
        self.proto.dataReceived(
            b"VALUE foo 0 3 12345\r\nval\r\nVALUE bar 1 4 123456\r\nue2\r\nEND\r\n"
        )
        self.assertEqual(
            self.successResultOf(d),
            {
                b"foo": (0, b"12345", b"val"),
                b"bar": (1, b"123456", b"ue2"),
            },
        )

    def test_add(self):
        """
        Test L{MemCacheProtocol.add}.
        """
        d = self.proto.add(b"foo", b"bar")
        self.assertEqual(self.tr.value(), b"add foo 0 0 3\r\nbar\r\n")
        self.proto.dataReceived(b"STORED\r\n")
        self.assertEqual(self.successResultOf(d), True)

    def test_addTimeout(self):
        """
        Test L{MemCacheProtocol.add} timeout.
        """
        self.proto.timeOut = 0.1
        d = self.proto.add(b"foo", b"bar")
        self.assertEqual(self.tr.value(), b"add foo 0 0 3\r\nbar\r\n")
        self.assertFalse(d.called)
        self.assertFailure(d, TimeoutError)
        self.assertEqual(self.tr.disconnectReason.type, TimeoutError)

    def test_addKeyTooLong(self):
        """
        Test L{MemCacheProtocol.add} with a key that is too long.
        """
        self.assertFailure(self.proto.add(b"x" * 251, b"bar"), ClientError)

    def test_addKeyWrongType(self):
        """
        Test L{MemCacheProtocol.add} with a key that is the wrong type.
        """
        self.assertFailure(self.proto.add(1, b"bar"), ClientError)

    def test_addValueWrongType(self):
        """
        Test L{MemCacheProtocol.add} with a value that is the wrong type.
        """
        self.assertFailure(self.proto.add(b"foo", 1), ClientError)

    def test_addNoConnection(self):
        """
        Test L{MemCacheProtocol.add} with no connection.
        """
        self.proto.transport.loseConnection()
        d = self.proto.add(b"foo", b"bar")
        self.assertEqual(self.tr.value(), b"add foo 0 0 3\r\nbar\r\n")
        self.assertFailure(d, RuntimeError)

    def test_addClientError(self):
        """
        Test L{MemCacheProtocol.add} with a client error.
        """
        d = self.proto.add(b"foo", b"bar")
        self.assertEqual(self.tr.value(), b"add foo 0 0 3\r\nbar\r\n")
        self.proto.dataReceived(b"CLIENT_ERROR test\r\n")
        self.assertFailure(d, ClientError)

    def test_addServerError(self):
        """
        Test L{MemCacheProtocol.add} with a server error.
        """
        d = self.proto.add(b"foo", b"bar")
        self.assertEqual(self.tr.value(), b"add foo 0 0 3\r\nbar\r\n")
        self.proto.dataReceived(b"SERVER_ERROR test\r\n")
        self.assertFailure(d, ServerError)

    def test_replace(self):
        """
        Test L{MemCacheProtocol.replace}.
        """
        d = self.proto.replace(b"foo", b"bar")
        self.assertEqual(self.tr.value(), b"replace foo 0 0 3\r\nbar\r\n")
        self.proto.dataReceived(b"STORED\r\n")
        self.assertEqual(self.successResultOf(d), True)

    def test_replaceTimeout(self):
        """
        Test L{MemCacheProtocol.replace} timeout.
        """
        self.proto.timeOut = 0.1
        d = self.proto.replace(b"foo", b"bar")
        self.assertEqual(self.tr.value(), b"replace foo 0 0 3\r\nbar\r\n")
        self.assertFalse(d.called)
        self.assertFailure(d, TimeoutError)
        self.assertEqual(self.tr.disconnectReason.type, TimeoutError)

    def test_replaceKeyTooLong(self):
        """
        Test L{MemCacheProtocol.replace} with a key that is too long.
        """
        self.assertFailure(self.proto.replace(b"x" * 251, b"bar"), ClientError)

    def test_replaceKeyWrongType(self):
        """
        Test L{MemCacheProtocol.replace} with a key that is the wrong type.
        """
        self.assertFailure(self.proto.replace(1, b"bar"), ClientError)

    def test_replaceValueWrongType(self):
        """
        Test L{MemCacheProtocol.replace} with a value that is the wrong type.
        """
        self.assertFailure(self.proto.replace(b"foo", 1), ClientError)

    def test_replaceNoConnection(self):
        """
        Test L{MemCacheProtocol.replace} with no connection.
        """
        self.proto.transport.loseConnection()
        d = self.proto.replace(b"foo", b"bar")
        self.assertEqual(self.tr.value(), b"replace foo 0 0 3\r\nbar\r\n")
        self.assertFailure(d, RuntimeError)

    def test_replaceClientError(self):
        """
        Test L{MemCacheProtocol.replace} with a client error.
        """
        d = self.proto.replace(b"foo", b"bar")
        self.assertEqual(self.tr.value(), b"replace foo 0 0 3\r\nbar\r\n")
        self.proto.dataReceived(b"CLIENT_ERROR test\r\n")
        self.assertFailure(d, ClientError)

    def test_replaceServerError(self):
        """
        Test L{MemCacheProtocol.replace} with a server error.
        """
        d = self.proto.replace(b"foo", b"bar")
        self.assertEqual(self.tr.value(), b"replace foo 0 0 3\r\nbar\r\n")
        self.proto.dataReceived(b"SERVER_ERROR test\r\n")
        self.assertFailure(d, ServerError)

    def test_checkAndSet(self):
        """
        Test L{MemCacheProtocol.checkAndSet}.
        """
        d = self.proto.checkAndSet(b"foo", b"bar", b"123")
        self.assertEqual(self.tr.value(), b"cas foo 0 0 3 123\r\nbar\r\n")
        self.proto.dataReceived(b"STORED\r\n")
        self.assertEqual(self.successResultOf(d), True)

    def test_checkAndSetTimeout(self):
        """
        Test L{MemCacheProtocol.checkAndSet} timeout.
        """
        self.proto.timeOut = 0.1
        d = self.proto.checkAndSet(b"foo", b"bar", b"123")
        self.assertEqual(self.tr.value(), b"cas foo 0 0 3 123\r\nbar\r\n")
        self.assertFalse(d.called)
        self.assertFailure(d, TimeoutError)
        self.assertEqual(self.tr.disconnectReason.type, TimeoutError)

    def test_checkAndSetKeyTooLong(self):
        """
        Test L{MemCacheProtocol.checkAndSet} with a key that is too long.
        """
        self.assertFailure(
            self.proto.checkAndSet(b"x" * 251, b"bar", b"123"), ClientError
        )

    def test_checkAndSetKeyWrongType(self):
        """
        Test L{MemCacheProtocol.checkAndSet} with a key that is the wrong type.
        """
        self.assertFailure(self.proto.checkAndSet(1, b"bar", b"123"), ClientError)

    def test_checkAndSetValueWrongType(self):
        """
        Test L{MemCacheProtocol.checkAndSet} with a value that is the wrong type.
        """
        self.assertFailure(self.proto.checkAndSet(b"foo", 1, b"123"), ClientError)

    def test_checkAndSetNoConnection(self):
        """
        Test L{MemCacheProtocol.checkAndSet} with no connection.
        """
        self.proto.transport.loseConnection()
        d = self.proto.checkAndSet(b"foo", b"bar", b"123")
        self.assertEqual(self.tr.value(), b"cas foo 0 0 3 123\r\nbar\r\n")
        self.assertFailure(d, RuntimeError)

    def test_checkAndSetClientError(self):
        """
        Test L{MemCacheProtocol.checkAndSet} with a client error.
        """
        d = self.proto.checkAndSet(b"foo", b"bar", b"123")
        self.assertEqual(self.tr.value(), b"cas foo 0 0 3 123\r\nbar\r\n")
        self.proto.dataReceived(b"CLIENT_ERROR test\r\n")
        self.assertFailure(d, ClientError)

    def test_checkAndSetServerError(self):
        """
        Test L{MemCacheProtocol.checkAndSet} with a server error.
        """
        d = self.proto.checkAndSet(b"foo", b"bar", b"123")
        self.assertEqual(self.tr.value(), b"cas foo 0 0 3 123\r\nbar\r\n")
        self.proto.dataReceived(b"SERVER_ERROR test\r\n")
        self.assertFailure(d, ServerError)

    def test_append(self):
        """
        Test L{MemCacheProtocol.append}.
        """
        d = self.proto.append(b"foo", b"bar")
        self.assertEqual(self.tr.value(), b"append foo 0 0 3\r\nbar\r\n")
        self.proto.dataReceived(b"STORED\r\n")
        self.assertEqual(self.successResultOf(d), True)

    def test_appendTimeout(self):
        """
        Test L{MemCacheProtocol.append} timeout.
        """
        self.proto.timeOut = 0.1
        d = self.proto.append(b"foo", b"bar")
        self.assertEqual(self.tr.value(), b"append foo 0 0 3\r\nbar\r\n")
        self.assertFalse(d.called)
        self.assertFailure(d, TimeoutError)
        self.assertEqual(self.tr.disconnectReason.type, TimeoutError)

    def test_appendKeyTooLong(self):
        """
        Test L{MemCacheProtocol.append} with a key that is too long.
        """
        self.assertFailure(self.proto.append(b"x" * 251, b"bar"), ClientError)

    def test_appendKeyWrongType(self):
        """
        Test L{MemCacheProtocol.append} with a key that is the wrong type.
        """
        self.assertFailure(self.proto.append(1, b"bar"), ClientError)

    def test_appendValueWrongType(self):
        """
        Test L{MemCacheProtocol.append} with a value that is the wrong type.
        """
        self.assertFailure(self.proto.append(b"foo", 1), ClientError)

    def test_appendNoConnection(self):
        """
        Test L{MemCacheProtocol.append} with no connection.
        """
        self.proto.transport.loseConnection()
        d = self.proto.append(b"foo", b"bar")
        self.assertEqual(self.tr.value(), b"append foo 0 0 3\r\nbar\r\n")
        self.assertFailure(d, RuntimeError)

    def test_appendClientError(self):
        """
        Test L{MemCacheProtocol.append} with a client error.
        """
        d = self.proto.append(b"foo", b"bar")
        self.assertEqual(self.tr.value(), b"append foo 0 0 3\r\nbar\r\n")
        self.proto.dataReceived(b"CLIENT_ERROR test\r\n")
        self.assertFailure(d, ClientError)

    def test_appendServerError(self):
        """
        Test L{MemCacheProtocol.append} with a server error.
        """
        d = self.proto.append(b"foo", b"bar")
        self.assertEqual(self.tr.value(), b"append foo 0 0 3\r\nbar\r\n")
        self.proto.dataReceived(b"SERVER_ERROR test\r\n")
        self.assertFailure(d, ServerError)

    def test_prepend(self):
        """
        Test L{MemCacheProtocol.prepend}.
        """
        d = self.proto.prepend(b"foo", b"bar")
        self.assertEqual(self.tr.value(), b"prepend foo 0 0 3\r\nbar\r\n")
        self.proto.dataReceived(b"STORED\r\n")
        self.assertEqual(self.successResultOf(d), True)

    def test_prependTimeout(self):
        """
        Test L{MemCacheProtocol.prepend} timeout.
        """
        self.proto.timeOut = 0.1
        d = self.proto.prepend(b"foo", b"bar")
        self.assertEqual(self.tr.value(), b"prepend foo 0 0 3\r\nbar\r\n")
        self.assertFalse(d.called)
        self.assertFailure(d, TimeoutError)
        self.assertEqual(self.tr.disconnectReason.type, TimeoutError)

    def test_prependKeyTooLong(self):
        """
        Test L{MemCacheProtocol.prepend} with a key that is too long.
        """
        self.assertFailure(self.proto.prepend(b"x" * 251, b"bar"), ClientError)

    def test_prependKeyWrongType(self):
        """
        Test L{MemCacheProtocol.prepend} with a key that is the wrong type.
        """
        self.assertFailure(self.proto.prepend(1, b"bar"), ClientError)

    def test_prependValueWrongType(self):
        """
        Test L{MemCacheProtocol.prepend} with a value that is the wrong type.
        """
        self.assertFailure(self.proto.prepend(b"foo", 1), ClientError)

    def test_prependNoConnection(self):
        """
        Test L{MemCacheProtocol.prepend} with no connection.
        """
        self.proto.transport.loseConnection()
        d = self.proto.prepend(b"foo", b"bar")
        self.assertEqual(self.tr.value(), b"prepend foo 0 0 3\r\nbar\r\n")
        self.assertFailure(d, RuntimeError)

    def test_prependClientError(self):
        """
        Test L{MemCacheProtocol.prepend} with a client error.
        """
        d = self.proto.prepend(b"foo", b"bar")
        self.assertEqual(self.tr.value(), b"prepend foo 0 0 3\r\nbar\r\n")
        self.proto.dataReceived(b"CLIENT_ERROR test\r\n")
        self.assertFailure(d, ClientError)

    def test_prependServerError(self):
        """
        Test L{MemCacheProtocol.prepend} with a server error.
        """
        d = self.proto.prepend(b"foo", b"bar")
        self.assertEqual(self.tr.value(), b"prepend foo 0 0 3\r\nbar\r\n")
        self.proto.dataReceived(b"SERVER_ERROR test\r\n")
        self.assertFailure(d, ServerError)

    def test_delete(self):
        """
        Test L{MemCacheProtocol.delete}.
        """
        d = self.proto.delete(b"foo")
        self.assertEqual(self.tr.value(), b"delete foo\r\n")
        self.proto.dataReceived(b"DELETED\r\n")
        self.assertEqual(self.successResultOf(d), True)

    def test_deleteTimeout(self):
        """
        Test L{MemCacheProtocol.delete} timeout.
        """
        self.proto.timeOut = 0.1
        d = self.proto.delete(b"foo")
        self.assertEqual(self.tr.value(), b"delete foo\r\n")
        self.assertFalse(d.called)
        self.assertFailure(d, TimeoutError)
        self.assertEqual(self.tr.disconnectReason.type, TimeoutError)

    def test_deleteKeyWrongType(self):
        """
        Test L{MemCacheProtocol.delete} with a key that is the wrong type.
        """
        self.assertFailure(self.proto.delete(1), ClientError)

    def test_deleteNoConnection(self):
        """
        Test L{MemCacheProtocol.delete} with no connection.
        """
        self.proto.transport.loseConnection()
        d = self.proto.delete(b"foo")
        self.assertEqual(self.tr.value(), b"delete foo\r\n")
        self.assertFailure(d, RuntimeError)

    def test_deleteNotFound(self):
        """
        Test L{MemCacheProtocol.delete} with a key that is not found.
        """
        d = self.proto.delete(b"foo")
        self.assertEqual(self.tr.value(), b"delete foo\r\n")
        self.proto.dataReceived(b"NOT_FOUND\r\n")
        self.assertEqual(self.successResultOf(d), False)

    def test_deleteClientError(self):
        """
        Test L{MemCacheProtocol.delete} with a client error.
        """
        d = self.proto.delete(b"foo")
        self.assertEqual(self.tr.value(), b"delete foo\r\n")
        self.proto.dataReceived(b"CLIENT_ERROR test\r\n")
        self.assertFailure(d, ClientError)

    def test_deleteServerError(self):
        """
        Test L{MemCacheProtocol.delete} with a server error.
        """
        d = self.proto.delete(b"foo")
        self.assertEqual(self.tr.value(), b"delete foo\r\n")
        self.proto.dataReceived(b"SERVER_ERROR test\r\n")
        self.assertFailure(d, ServerError)

    def test_increment(self):
        """
        Test L{MemCacheProtocol.increment}.
        """
        d = self.proto.increment(b"foo")
        self.assertEqual(self.tr.value(), b"incr foo 1\r\n")
        self.proto.dataReceived(b"123\r\n")
        self.assertEqual(self.successResultOf(d), 123)

    def test_incrementTimeout(self):
        """
        Test L{MemCacheProtocol.increment} timeout.
        """
        self.proto.timeOut = 0.1
        d = self.proto.increment(b"foo")
        self.assertEqual(self.tr.value(), b"incr foo 1\r\n")
        self.assertFalse(d.called)
        self.assertFailure(d, TimeoutError)
        self.assertEqual(self.tr.disconnectReason.type, TimeoutError)

    def test_incrementKeyTooLong(self):
        """
        Test L{MemCacheProtocol.increment} with a key that is too long.
        """
        self.assertFailure(self.proto.increment(b"x" * 251), ClientError)

    def test_incrementKeyWrongType(self):
        """
        Test L{MemCacheProtocol.increment} with a key that is the wrong type.
        """
        self.assertFailure(self.proto.increment(1), ClientError)

    def test_incrementNoConnection(self):
        """
        Test L{MemCacheProtocol.increment} with no connection.
        """
        self.proto.transport.loseConnection()
        d = self.proto.increment(b"foo")
        self.assertEqual(self.tr.value(), b"incr foo 1\r\n")
        self.assertFailure(d, RuntimeError)

    def test_incrementNotFound(self):
        """
        Test L{MemCacheProtocol.increment} with a key that is not found.
        """
        d = self.proto.increment(b"foo")
        self.assertEqual(self.tr.value(), b"incr foo 1\r\n")
        self.proto.dataReceived(b"NOT_FOUND\r\n")
        self.assertEqual(self.successResultOf(d), False)

    def test_incrementClientError(self):
        """
        Test L{MemCacheProtocol.increment} with a client error.
        """
        d = self.proto.increment(b"foo")
        self.assertEqual(self.tr.value(), b"incr foo 1\r\n")
        self.proto.dataReceived(b"CLIENT_ERROR test\r\n")
        self.assertFailure(d, ClientError)

    def test_incrementServerError(self):
        """
        Test L{MemCacheProtocol.increment} with a server error.
        """
        d = self.proto.increment(b"foo")
        self.assertEqual(self.tr.value(), b"incr foo 1\r\n")
        self.proto.dataReceived(b"SERVER_ERROR test\r\n")
        self.assertFailure(d, ServerError)

    def test_decrement(self):
        """
        Test L{MemCacheProtocol.decrement}.
        """
        d = self.proto.decrement(b"foo")
        self.assertEqual(self.tr.value(), b"decr foo 1\r\n")
        self.proto.dataReceived(b"123\r\n")
        self.assertEqual(self.successResultOf(d), 123)

    def test_decrementTimeout(self):
        """
        Test L{MemCacheProtocol.decrement} timeout.
        """
        self.proto.timeOut = 0.1
        d = self.proto.decrement(b"foo")
        self.assertEqual(self.tr.value(), b"decr foo 1\r\n")
        self.assertFalse(d.called)
        self.assertFailure(d, TimeoutError)
        self.assertEqual(self.tr.disconnectReason.type, TimeoutError)

    def test_decrementKeyTooLong(self):
        """
        Test L{MemCacheProtocol.decrement} with a key that is too long.
        """
        self.assertFailure(self.proto.decrement(b"x" * 251), ClientError)

    def test_decrementKeyWrongType(self):
        """
        Test L{MemCacheProtocol.decrement} with a key that is the wrong type.
        """
        self.assertFailure(self.proto.decrement(1), ClientError)

    def test_decrementNoConnection(self):
        """
        Test L{MemCacheProtocol.decrement} with no connection.
        """
        self.proto.transport.loseConnection()
        d = self.proto.decrement(b"foo")
        self.assertEqual(self.tr.value(), b"decr foo 1\r\n")
        self.assertFailure(d, RuntimeError)

    def test_decrementNotFound(self):
        """
        Test L{MemCacheProtocol.decrement} with a key that is not found.
        """
        d = self.proto.decrement(b"foo")
        self.assertEqual(self.tr.value(), b"decr foo 1\r\n")
        self.proto.dataReceived(b"NOT_FOUND\r\n")
        self.assertEqual(self.successResultOf(d), False)

    def test_decrementClientError(self):
        """
        Test L{MemCacheProtocol.decrement} with a client error.
        """
        d = self.proto.decrement(b"foo")
        self.assertEqual(self.tr.value(), b"decr foo 1\r\n")
        self.proto.dataReceived(b"CLIENT_ERROR test\r\n")
        self.assertFailure(d, ClientError)

    def test_decrementServerError(self):
        """
        Test L{MemCacheProtocol.decrement} with a server error.
        """
        d = self.proto.decrement(b"foo")
        self.assertEqual(self.tr.value(), b"decr foo 1\r\n")
        self.proto.dataReceived(b"SERVER_ERROR test\r\n")
        self.assertFailure(d, ServerError)

    def test_stats(self):
        """
        Test L{MemCacheProtocol.stats}.
        """
        d = self.proto.stats()
        self.assertEqual(self.tr.value(), b"stats\r\n")
        self.proto.dataReceived(b"STAT foo 123\r\nEND\r\n")
        self.assertEqual(self.successResultOf(d), {b"foo": b"123"})

    def test_statsTimeout(self):
        """
        Test L{MemCacheProtocol.stats} timeout.
        """
        self.proto.timeOut = 0.1
        d = self.proto.stats()
        self.assertEqual(self.tr.value(), b"stats\r\n")
        self.assertFalse(d.called)
        self.assertFailure(d, TimeoutError)
        self.assertEqual(self.tr.disconnectReason.type, TimeoutError)

    def test_statsNoConnection(self):
        """
        Test L{MemCacheProtocol.stats} with no connection.
        """
        self.proto.transport.loseConnection()
        d = self.proto.stats()
        self.assertEqual(self.tr.value(), b"stats\r\n")
        self.assertFailure(d, RuntimeError)

    def test_statsClientError(self):
        """
        Test L{MemCacheProtocol.stats} with a client error.
        """
        d = self.proto.stats()
        self.assertEqual(self.tr.value(), b"stats\r\n")
        self.proto.dataReceived(b"CLIENT_ERROR test\r\n")
        self.assertFailure(d, ClientError)

    def test_statsServerError(self):
        """
        Test L{MemCacheProtocol.stats} with a server error.
        """
        d = self.proto.stats()
        self.assertEqual(self.tr.value(), b"stats\r\n")
        self.proto.dataReceived(b"SERVER_ERROR test\r\n")
        self.assertFailure(d, ServerError)

    def test_version(self):
        """
        Test L{MemCacheProtocol.version}.
        """
        d = self.proto.version()
        self.assertEqual(self.tr.value(), b"version\r\n")
        self.proto.dataReceived(b"VERSION test\r\n")
        self.assertEqual(self.successResultOf(d), b"test")

    def test_versionTimeout(self):
        """
        Test L{MemCacheProtocol.version} timeout.
        """
        self.proto.timeOut = 0.1
        d = self.proto.version()
        self.assertEqual(self.tr.value(), b"version\r\n")
        self.assertFalse(d.called)
        self.assertFailure(d, TimeoutError)
        self.assertEqual(self.tr.disconnectReason.type, TimeoutError)

    def test_versionNoConnection(self):
        """
        Test L{MemCacheProtocol.version} with no connection.
        """
        self.proto.transport.loseConnection()
        d = self.proto.version()
        self.assertEqual(self.tr.value(), b"version\r\n")
        self.assertFailure(d, RuntimeError)

    def test_versionClientError(self):
        """
        Test L{MemCacheProtocol.version} with a client error.
        """
        d = self.proto.version()
        self.assertEqual(self.tr.value(), b"version\r\n")
        self.proto.dataReceived(b"CLIENT_ERROR test\r\n")
        self.assertFailure(d, ClientError)

    def test_versionServerError(self):
        """
        Test L{MemCacheProtocol.version} with a server error.
        """
        d = self.proto.version()
        self.assertEqual(self.tr.value(), b"version\r\n")
        self.proto.dataReceived(b"SERVER_ERROR test\r\n")
        self.assertFailure(d, ServerError)

    def test_flushAll(self):
        """
        Test L{MemCacheProtocol.flushAll}.
        """
        d = self.proto.flushAll()
        self.assertEqual(self.tr.value(), b"flush_all\r\n")
        self.proto.dataReceived(b"OK\r\n")
        self.assertEqual(self.successResultOf(d), True)

    def test_flushAllTimeout(self):
        """
        Test L{MemCacheProtocol.flushAll} timeout.
        """
        self.proto.timeOut = 0.1
        d = self.proto.flushAll()
        self.assertEqual(self.tr.value(), b"flush_all\r\n")
        self.assertFalse(d.called)
        self.assertFailure(d, TimeoutError)
        self.assertEqual(self.tr.disconnectReason.type, TimeoutError)

    def test_flushAllNoConnection(self):
        """
        Test L{MemCacheProtocol.flushAll} with no connection.
        """
        self.proto.transport.loseConnection()
        d = self.proto.flushAll()
        self.assertEqual(self.tr.value(), b"flush_all\r\n")
        self.assertFailure(d, RuntimeError)

    def test_flushAllClientError(self):
        """
        Test L{MemCacheProtocol.flushAll} with a client error.
        """
        d = self.proto.flushAll()
        self.assertEqual(self.tr.value(), b"flush_all\r\n")
        self.proto.dataReceived(b"CLIENT_ERROR test\r\n")
        self.assertFailure(d, ClientError)

    def test_flushAllServerError(self):
        """
        Test L{MemCacheProtocol.flushAll} with a server error.
        """
        d = self.proto.flushAll()
        self.assertEqual(self.tr.value(), b"flush_all\r\n")
        self.proto.dataReceived(b"SERVER_ERROR test\r\n")
        self.assertFailure(d, ServerError)


class MemCacheErrorHandlingTests(unittest.TestCase):
    """
    Tests for L{MemCacheProtocol}'s error handling.
    """

    def setUp(self):
        """
        Initialize the protocol and mock transport.
        """
        self.proto = MemCacheProtocol()
        self.tr = FakeTransport()
        self.proto.makeConnection(self.tr)

    def tearDown(self):
        """
        Disconnect the protocol.
        """
        self.proto.connectionLost(Failure(ConnectionDone()))

    def test_clientError(self):
        """
        Test L{MemCacheProtocol.lineReceived} handling a client error.
        """
        d = self.proto.set(b"foo", b"bar")
        self.proto.lineReceived(b"CLIENT_ERROR test")
        self.assertFailure(d, ClientError)

    def test_serverError(self):
        """
        Test L{MemCacheProtocol.lineReceived} handling a server error.
        """
        d = self.proto.set(b"foo", b"bar")
        self.proto.lineReceived(b"SERVER_ERROR test")
        self.assertFailure(d, ServerError)

    def test_nonExistentCommand(self):
        """
        Test L{MemCacheProtocol.lineReceived} handling a non-existent command.
        """
        d = self.proto.set(b"foo", b"bar")
        self.proto.lineReceived(b"ERROR")
        self.assertFailure(d, Exception)

    def test_unexpectedEndResponse(self):
        """
        Test L{MemCacheProtocol.lineReceived} handling an unexpected END
        response.
        """
        d = self.proto.set(b"foo", b"bar")
        self.proto.lineReceived(b"END")
        self.assertFailure(d, RuntimeError)

    def test_unexpectedValueResponse(self):
        """
        Test L{MemCacheProtocol.lineReceived} handling an unexpected VALUE
        response.
        """
        d = self.proto.set(b"foo", b"bar")
        self.proto.lineReceived(b"VALUE foo 0 3")
        self.assertFailure(d, RuntimeError)

    def test_unexpectedResponse(self):
        """
        Test L{MemCacheProtocol.lineReceived} handling an unexpected response.
        """
        d = self.proto.set(b"foo", b"bar")
        self.proto.lineReceived(b"UNKNOWN")
        self.assertFailure(d, RuntimeError)


class MemCacheCancelTests(unittest.TestCase):
    """
    Tests for L{MemCacheProtocol}'s cancellation.
    """

    def setUp(self):
        """
        Initialize the protocol and mock transport.
        """
        self.proto = MemCacheProtocol()
        self.tr = FakeTransport()
        self.proto.makeConnection(self.tr)

    def tearDown(self):
        """
        Disconnect the protocol.
        """
        self.proto.connectionLost(Failure(ConnectionDone()))

    def test_cancel(self):
        """
        Test cancelling a L{MemCacheProtocol} operation.
        """
        d = self.proto.set(b"foo", b"bar")
        self.proto.set(b"foo", b"bar")
        self.assertEqual(len(self.proto._current), 2)
        d.cancel()
        self.assertEqual(len(self.proto._current), 1)
        d.addErrback(lambda f: f.trap(CancelledError))
        self.assertEqual(self.proto._current[0].command, b"set")

    def test_cancelNoConnection(self):
        """
        Test cancelling a L{MemCacheProtocol} operation with no connection.
        """
        self.proto.transport.loseConnection()
        d = self.proto.set(b"foo", b"bar")
        self.assertFailure(d, RuntimeError)
        d.cancel()
        self.assertFailure(d, RuntimeError)

    def test_cancelTimeout(self):
        """
        Test cancelling a L{MemCacheProtocol} operation with a timeout.
        """
        self.proto.timeOut = 0.1
        d = self.proto.set(b"foo", b"bar")
        self.assertEqual(self.tr.value(), b"set foo 0 0 3\r\nbar\r\n")
        self.assertFalse(d.called)
        self.assertFailure(d, TimeoutError)
        self.assertEqual(self.tr.disconnectReason.type, TimeoutError)
        d.cancel()
        self.assertFailure(d, TimeoutError)


class MemCacheConnectionTests(unittest.TestCase):
    """
    Tests for L{MemCacheProtocol}'s connection handling.
    """

    def setUp(self):
        """
        Initialize the protocol and mock transport.
        """
        self.proto = MemCacheProtocol()
        self.tr = FakeTransport()
        self.proto.makeConnection(self.tr)

    def tearDown(self):
        """
        Disconnect the protocol.
        """
        self.proto.connectionLost(Failure(ConnectionDone()))

    def test_connectionLost(self):
        """
        Test L{MemCacheProtocol.connectionLost}.
        """
        d = self.proto.set(b"foo", b"bar")
        self.proto.connectionLost(Failure(ConnectionLost()))
        self.assertFailure(d, ConnectionLost)

    def test_connectionLostNoConnection(self):
        """
        Test L{MemCacheProtocol.connectionLost} with no connection.
        """
        self.proto.transport.loseConnection()
        d = self.proto.set(b"foo", b"bar")
        self.assertFailure(d, RuntimeError)
        self.proto.connectionLost(Failure(ConnectionLost()))
        self.assertFailure(d, RuntimeError)


class MemCacheFactoryTests(unittest.TestCase):
    """
    Tests for L{ClientFactory}.
    """

    def test_buildProtocol(self):
        """
        Test L{ClientFactory.buildProtocol}.
        """
        factory = ClientFactory()
        proto = factory.buildProtocol(None)
        self.assertIsInstance(proto, MemCacheProtocol)


class FakeTransport:
    """
    A fake transport for use in testing L{MemCacheProtocol}.

    @ivar disconnectReason: L{Failure} indicating the reason for disconnection.
    """

    disconnecting = False
    disconnectReason = None

    def __init__(self):
        self.data = []

    def value(self):
        return b"".join(self.data)

    def write(self, data):
        self.data.append(data)

    def loseConnection(self):
        self.disconnecting = True
        self.disconnectReason = Failure(ConnectionDone())