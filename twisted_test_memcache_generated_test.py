# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

import time
from collections import defaultdict
from unittest import TestCase

from twisted.internet.defer import Deferred, fail, succeed
from twisted.python.failure import Failure
from twisted.protocols.memcache import (
    DEFAULT_PORT,
    MemCacheProtocol,
    NoSuchCommand,
    ClientError,
    ServerError,
)
from twisted.test.proto_helpers import MemoryReactor, StringTransport


class MemCacheTestCase(TestCase):
    def setUp(self):
        self.proto = MemCacheProtocol()
        self.tr = StringTransport()
        self.proto.makeConnection(self.tr)
        self.proto.timeOut = None

    def tearDown(self):
        self.proto.connectionLost("tearDown")

    def test_get(self):
        """
        L{MemCacheProtocol.get} allows to retrieve a key in the memcached
        server.
        """
        d = self.proto.get(b"key")

        self.assertEqual(b"get key\r\n", self.tr.value())
        self.proto.lineReceived(b"VALUE key 42 5")
        self.proto.rawDataReceived(b"HELLO\r\n")
        self.proto.lineReceived(b"END")

        def cb(value):
            self.assertEqual((42, b"HELLO"), value)

        return d.addCallback(cb)

    def test_getEmpty(self):
        """
        L{MemCacheProtocol.get} returns C{None} and C{0} if the key is not
        present in the server.
        """
        d = self.proto.get(b"key")

        self.assertEqual(b"get key\r\n", self.tr.value())
        self.proto.lineReceived(b"END")

        def cb(value):
            self.assertEqual((0, None), value)

        return d.addCallback(cb)

    def test_getInvalidKey(self):
        """
        L{MemCacheProtocol.get} fails when given an invalid key.
        """
        d = self.proto.get("key")
        self.failureResultOf(d, ClientError)

        return d.addErrback(
            lambda e: self.assertEqual(
                str(e.value), "Invalid type for key: <class 'str'>, expecting bytes"
            )
        )

    def test_getKeyTooLong(self):
        """
        L{MemCacheProtocol.get} fails when given a key that is too long.
        """
        d = self.proto.get(b"x" * 251)
        self.failureResultOf(d, ClientError)

        return d.addErrback(
            lambda e: self.assertEqual(
                str(e.value), "Key too long",
            )
        )

    def test_getMultiple(self):
        """
        L{MemCacheProtocol.getMultiple} allows to retrieve multiple keys
        at once in the memcached server.
        """
        d = self.proto.getMultiple([b"key", b"key2"])

        self.assertEqual(b"get key key2\r\n", self.tr.value())
        self.proto.lineReceived(b"VALUE key 42 5")
        self.proto.rawDataReceived(b"HELLO\r\n")
        self.proto.lineReceived(b"VALUE key2 0 2")
        self.proto.rawDataReceived(b"ok\r\n")
        self.proto.lineReceived(b"END")

        def cb(values):
            self.assertEqual({b"key": (42, b"HELLO"), b"key2": (0, b"ok")}, values)

        return d.addCallback(cb)

    def test_getMultipleEmpty(self):
        """
        L{MemCacheProtocol.getMultiple} returns C{None} and C{0} for
        each key that is not present in the server.
        """
        d = self.proto.getMultiple([b"key", b"key2"])

        self.assertEqual(b"get key key2\r\n", self.tr.value())
        self.proto.lineReceived(b"END")

        def cb(values):
            self.assertEqual({b"key": (0, None), b"key2": (0, None)}, values)

        return d.addCallback(cb)

    def test_getMultipleInvalidKey(self):
        """
        L{MemCacheProtocol.getMultiple} fails when given an invalid key.
        """
        d = self.proto.getMultiple(["key"])
        self.failureResultOf(d, ClientError)

        return d.addErrback(
            lambda e: self.assertEqual(
                str(e.value), "Invalid type for key: <class 'str'>, expecting bytes"
            )
        )

    def test_getMultipleKeyTooLong(self):
        """
        L{MemCacheProtocol.getMultiple} fails when given a key that is too long.
        """
        d = self.proto.getMultiple([b"x" * 251])
        self.failureResultOf(d, ClientError)

        return d.addErrback(
            lambda e: self.assertEqual(
                str(e.value), "Key too long",
            )
        )

    def test_gets(self):
        """
        L{MemCacheProtocol.get} returns a unique identifier along with the
        value if C{withIdentifier} is set to C{True}.
        """
        d = self.proto.get(b"key", withIdentifier=True)

        self.assertEqual(b"gets key\r\n", self.tr.value())
        self.proto.lineReceived(b"VALUE key 42 5 47")
        self.proto.rawDataReceived(b"HELLO\r\n")
        self.proto.lineReceived(b"END")

        def cb(value):
            self.assertEqual((42, b"47", b"HELLO"), value)

        return d.addCallback(cb)

    def test_getsMultiple(self):
        """
        L{MemCacheProtocol.getMultiple} returns a unique identifier along
        with each value if C{withIdentifier} is set to C{True}.
        """
        d = self.proto.getMultiple([b"key", b"key2"], withIdentifier=True)

        self.assertEqual(b"gets key key2\r\n", self.tr.value())
        self.proto.lineReceived(b"VALUE key 42 5 47")
        self.proto.rawDataReceived(b"HELLO\r\n")
        self.proto.lineReceived(b"VALUE key2 0 2 1")
        self.proto.rawDataReceived(b"ok\r\n")
        self.proto.lineReceived(b"END")

        def cb(values):
            self.assertEqual(
                {b"key": (42, b"47", b"HELLO"), b"key2": (0, b"1", b"ok")}, values
            )

        return d.addCallback(cb)

    def test_set(self):
        """
        L{MemCacheProtocol.set} stores a key/value pair in the memcached
        server.
        """
        d = self.proto.set(b"key", b"value", 44, 3)

        self.assertEqual(b"set key 44 3 5\r\nvalue\r\n", self.tr.value())
        self.proto.lineReceived(b"STORED")

        return d.addCallback(self.assertTrue)

    def test_setInvalidKey(self):
        """
        L{MemCacheProtocol.set} fails when given an invalid key.
        """
        d = self.proto.set("key", b"value")
        self.failureResultOf(d, ClientError)

        return d.addErrback(
            lambda e: self.assertEqual(
                str(e.value), "Invalid type for key: <class 'str'>, expecting bytes"
            )
        )

    def test_setKeyTooLong(self):
        """
        L{MemCacheProtocol.set} fails when given a key that is too long.
        """
        d = self.proto.set(b"x" * 251, b"value")
        self.failureResultOf(d, ClientError)

        return d.addErrback(
            lambda e: self.assertEqual(
                str(e.value), "Key too long",
            )
        )

    def test_setInvalidValue(self):
        """
        L{MemCacheProtocol.set} fails when given an invalid value.
        """
        d = self.proto.set(b"key", "value")
        self.failureResultOf(d, ClientError)

        return d.addErrback(
            lambda e: self.assertEqual(
                str(e.value),
                "Invalid type for value: <class 'str'>, expecting bytes",
            )
        )

    def test_add(self):
        """
        L{MemCacheProtocol.add} adds a key/value pair in the memcached
        server.
        """
        d = self.proto.add(b"key", b"value", 44, 3)

        self.assertEqual(b"add key 44 3 5\r\nvalue\r\n", self.tr.value())
        self.proto.lineReceived(b"STORED")

        return d.addCallback(self.assertTrue)

    def test_replace(self):
        """
        L{MemCacheProtocol.replace} replaces a key/value pair in the
        memcached server.
        """
        d = self.proto.replace(b"key", b"value", 44, 3)

        self.assertEqual(b"replace key 44 3 5\r\nvalue\r\n", self.tr.value())
        self.proto.lineReceived(b"STORED")

        return d.addCallback(self.assertTrue)

    def test_replaceWithNonExistentKey(self):
        """
        L{MemCacheProtocol.replace} returns C{False} if the key doesn't
        previously exist in the memcached server.
        """
        d = self.proto.replace(b"key", b"value", 44, 3)

        self.assertEqual(b"replace key 44 3 5\r\nvalue\r\n", self.tr.value())
        self.proto.lineReceived(b"NOT_STORED")

        return d.addCallback(self.assertFalse)

    def test_checkAndSet(self):
        """
        L{MemCacheProtocol.checkAndSet} replaces a key/value pair in the
        memcached server only if the unique identifier matches the current
        one.
        """
        d = self.proto.checkAndSet(b"key", b"value", b"47", 44, 3)

        self.assertEqual(b"cas key 44 3 5 47\r\nvalue\r\n", self.tr.value())
        self.proto.lineReceived(b"STORED")

        return d.addCallback(self.assertTrue)

    def test_checkAndSetFailed(self):
        """
        L{MemCacheProtocol.checkAndSet} returns C{False} if the unique
        identifier doesn't match the current one.
        """
        d = self.proto.checkAndSet(b"key", b"value", b"47", 44, 3)

        self.assertEqual(b"cas key 44 3 5 47\r\nvalue\r\n", self.tr.value())
        self.proto.lineReceived(b"EXISTS")

        return d.addCallback(self.assertFalse)

    def test_append(self):
        """
        L{MemCacheProtocol.append} allows to append data to a value in the
        server.
        """
        d = self.proto.append(b"key", b"value")

        self.assertEqual(b"append key 0 0 5\r\nvalue\r\n", self.tr.value())
        self.proto.lineReceived(b"STORED")

        return d.addCallback(self.assertTrue)

    def test_prepend(self):
        """
        L{MemCacheProtocol.prepend} allows to prepend data to a value in the
        server.
        """
        d = self.proto.prepend(b"key", b"value")

        self.assertEqual(b"prepend key 0 0 5\r\nvalue\r\n", self.tr.value())
        self.proto.lineReceived(b"STORED")

        return d.addCallback(self.assertTrue)

    def test_delete(self):
        """
        L{MemCacheProtocol.delete} allows to delete a key/value pair from the
        server.
        """
        d = self.proto.delete(b"key")

        self.assertEqual(b"delete key\r\n", self.tr.value())
        self.proto.lineReceived(b"DELETED")

        return d.addCallback(self.assertTrue)

    def test_deleteWithNonExistentKey(self):
        """
        L{MemCacheProtocol.delete} returns C{False} if the key doesn't exist
        in the server.
        """
        d = self.proto.delete(b"key")

        self.assertEqual(b"delete key\r\n", self.tr.value())
        self.proto.lineReceived(b"NOT_FOUND")

        return d.addCallback(self.assertFalse)

    def test_deleteInvalidKey(self):
        """
        L{MemCacheProtocol.delete} fails when given an invalid key.
        """
        d = self.proto.delete("key")
        self.failureResultOf(d, ClientError)

        return d.addErrback(
            lambda e: self.assertEqual(
                str(e.value), "Invalid type for key: <class 'str'>, expecting bytes"
            )
        )

    def test_deleteKeyTooLong(self):
        """
        L{MemCacheProtocol.delete} fails when given a key that is too long.
        """
        d = self.proto.delete(b"x" * 251)
        self.failureResultOf(d, ClientError)

        return d.addErrback(
            lambda e: self.assertEqual(
                str(e.value), "Key too long",
            )
        )

    def test_incr(self):
        """
        L{MemCacheProtocol.increment} allows to increment a value in the
        server.
        """
        d = self.proto.increment(b"key", 3)

        self.assertEqual(b"incr key 3\r\n", self.tr.value())
        self.proto.lineReceived(b"8")

        def cb(value):
            self.assertEqual(8, value)

        return d.addCallback(cb)

    def test_incrWithNonExistentKey(self):
        """
        L{MemCacheProtocol.increment} returns C{False} if the key doesn't
        exist in the server.
        """
        d = self.proto.increment(b"key", 3)

        self.assertEqual(b"incr key 3\r\n", self.tr.value())
        self.proto.lineReceived(b"NOT_FOUND")

        return d.addCallback(self.assertFalse)

    def test_incrInvalidKey(self):
        """
        L{MemCacheProtocol.increment} fails when given an invalid key.
        """
        d = self.proto.increment("key")
        self.failureResultOf(d, ClientError)

        return d.addErrback(
            lambda e: self.assertEqual(
                str(e.value), "Invalid type for key: <class 'str'>, expecting bytes"
            )
        )

    def test_incrKeyTooLong(self):
        """
        L{MemCacheProtocol.increment} fails when given a key that is too long.
        """
        d = self.proto.increment(b"x" * 251)
        self.failureResultOf(d, ClientError)

        return d.addErrback(
            lambda e: self.assertEqual(
                str(e.value), "Key too long",
            )
        )

    def test_decr(self):
        """
        L{MemCacheProtocol.decrement} allows to decrement a value in the
        server.
        """
        d = self.proto.decrement(b"key", 3)

        self.assertEqual(b"decr key 3\r\n", self.tr.value())
        self.proto.lineReceived(b"8")

        def cb(value):
            self.assertEqual(8, value)

        return d.addCallback(cb)

    def test_decrWithNonExistentKey(self):
        """
        L{MemCacheProtocol.decrement} returns C{False} if the key doesn't
        exist in the server.
        """
        d = self.proto.decrement(b"key", 3)

        self.assertEqual(b"decr key 3\r\n", self.tr.value())
        self.proto.lineReceived(b"NOT_FOUND")

        return d.addCallback(self.assertFalse)

    def test_decrInvalidKey(self):
        """
        L{MemCacheProtocol.decrement} fails when given an invalid key.
        """
        d = self.proto.decrement("key")
        self.failureResultOf(d, ClientError)

        return d.addErrback(
            lambda e: self.assertEqual(
                str(e.value), "Invalid type for key: <class 'str'>, expecting bytes"
            )
        )

    def test_decrKeyTooLong(self):
        """
        L{MemCacheProtocol.decrement} fails when given a key that is too long.
        """
        d = self.proto.decrement(b"x" * 251)
        self.failureResultOf(d, ClientError)

        return d.addErrback(
            lambda e: self.assertEqual(
                str(e.value), "Key too long",
            )
        )

    def test_version(self):
        """
        L{MemCacheProtocol.version} allows to retrieve the version of the
        server.
        """
        d = self.proto.version()

        self.assertEqual(b"version\r\n", self.tr.value())
        self.proto.lineReceived(b"VERSION 1.0")

        def cb(value):
            self.assertEqual(b"1.0", value)

        return d.addCallback(cb)

    def test_disconnect(self):
        """
        L{MemCacheProtocol} fires the errback if the connection is lost.
        """
        d = self.proto.get(b"key")
        self.proto.connectionLost(None)
        return self.assertFailure(d, Exception)

    def test_noSuchCommand(self):
        """
        L{MemCacheProtocol} fires the errback with a L{NoSuchCommand}
        exception if a non-existent command is sent.
        """
        d = self.proto.get(b"key")
        self.proto.lineReceived(b"ERROR")
        return self.assertFailure(d, NoSuchCommand)

    def test_clientError(self):
        """
        L{MemCacheProtocol} fires the errback with a L{ClientError} exception
        if an invalid input is sent.
        """
        d = self.proto.get(b"key")
        self.proto.lineReceived(b"CLIENT_ERROR invalid")
        return self.assertFailure(d, ClientError)

    def test_serverError(self):
        """
        L{MemCacheProtocol} fires the errback with a L{ServerError} exception
        if an error occurs server-side.
        """
        d = self.proto.get(b"key")
        self.proto.lineReceived(b"SERVER_ERROR invalid")
        return self.assertFailure(d, ServerError)

    def test_stats(self):
        """
        L{MemCacheProtocol.stats} allows to get stats from the server.
        """
        d = self.proto.stats()

        self.assertEqual(b"stats\r\n", self.tr.value())
        self.proto.lineReceived(b"STAT key value")
        self.proto.lineReceived(b"STAT key2 value2")
        self.proto.lineReceived(b"END")

        def cb(value):
            self.assertEqual({b"key": b"value", b"key2": b"value2"}, value)

        return d.addCallback(cb)

    def test_statsWithArg(self):
        """
        L{MemCacheProtocol.stats} allows to send an optional string along
        with the command.
        """
        d = self.proto.stats(b"slabs")

        self.assertEqual(b"stats slabs\r\n", self.tr.value())
        self.proto.lineReceived(b"STAT key value")
        self.proto.lineReceived(b"STAT key2 value2")
        self.proto.lineReceived(b"END")

        def cb(value):
            self.assertEqual({b"key": b"value", b"key2": b"value2"}, value)

        return d.addCallback(cb)

    def test_flushAll(self):
        """
        L{MemCacheProtocol.flushAll} allows to flush all cached values.
        """
        d = self.proto.flushAll()

        self.assertEqual(b"flush_all\r\n", self.tr.value())
        self.proto.lineReceived(b"OK")

        return d.addCallback(self.assertTrue)

    def test_timeout(self):
        """
        L{MemCacheProtocol} closes the connection if the timeout is reached.
        """
        self.proto.persistentTimeOut = 1
        self.proto.get(b"key")
        self.proto.timeoutConnection()
        self.assertEqual(self.tr.disconnecting, True)


class TimeoutTests(TestCase):
    """
    Tests for the timeout behavior of L{MemCacheProtocol}.
    """

    def setUp(self):
        self.reactor = MemoryReactor()
        self.proto = MemCacheProtocol()
        self.proto.persistentTimeOut = 4
        self.tr = StringTransport()
        self.proto.makeConnection(self.tr)

    def test_timeout(self):
        """
        L{MemCacheProtocol} times out if a command is sent and no
        response is received.
        """
        self.proto.increment(b"key")
        self.assertEqual(self.reactor.getDelayedCalls(), [])
        self.reactor.advance(3)
        self.assertEqual(self.reactor.getDelayedCalls(), [])
        self.reactor.advance(1)
        self.assertTrue(self.tr.disconnecting)

    def test_timeoutReset(self):
        """
        L{MemCacheProtocol} resets the timeout if data is received.
        """
        self.proto.increment(b"key")
        self.reactor.advance(2)
        self.proto.rawDataReceived(b"test")
        self.reactor.advance(2)
        self.assertEqual(self.reactor.getDelayedCalls(), [])
        self.reactor.advance(2)
        self.assertTrue(self.tr.disconnecting)

    def test_timeoutCancel(self):
        """
        L{MemCacheProtocol} cancels the timeout if the command is
        completed.
        """
        self.proto.increment(b"key")
        self.reactor.advance(2)
        self.proto.lineReceived(b"4")
        self.reactor.advance(2)
        self.assertEqual(self.reactor.getDelayedCalls(), [])
        self.assertFalse(self.tr.disconnecting)


class TimeoutMixinTests(TestCase):
    """
    Tests for the C{TimeoutMixin} class.
    """

    def setUp(self):
        self.reactor = MemoryReactor()
        self.proto = MemCacheProtocol()
        self.proto.timeOut = 4
        self.tr = StringTransport()
        self.proto.makeConnection(self.tr)

    def test_connectionTimeout(self):
        """
        L{MemCacheProtocol} times out if the connection is made and no
        command is sent.
        """
        self.reactor.advance(3)
        self.assertEqual(self.reactor.getDelayedCalls(), [])
        self.reactor.advance(1)
        self.assertTrue(self.tr.disconnecting)

    def test_connectionTimeoutReset(self):
        """
        L{MemCacheProtocol} resets the timeout if a command is sent.
        """
        self.reactor.advance(2)
        self.proto.increment(b"key")
        self.reactor.advance(2)
        self.assertEqual(self.reactor.getDelayedCalls(), [])
        self.reactor.advance(2)
        self.assertTrue(self.tr.disconnecting)

    def test_connectionTimeoutCancel(self):
        """
        L{MemCacheProtocol} cancels the timeout if the connection is
        lost.
        """
        self.reactor.advance(2)
        self.proto.connectionLost(None)
        self.reactor.advance(2)
        self.assertEqual(self.reactor.getDelayedCalls(), [])
        self.assertFalse(self.tr.disconnecting)