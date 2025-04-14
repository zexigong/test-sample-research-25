# -*- test-case-name: twisted.test.test_memcache -*-
# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

import unittest
from twisted.internet.defer import Deferred
from twisted.test.proto_helpers import MemoryReactor
from twisted.protocols.memcache import (
    MemCacheProtocol,
    NoSuchCommand,
    ClientError,
    ServerError,
    Command,
)


class MemCacheProtocolTestCase(unittest.TestCase):
    def setUp(self):
        self.reactor = MemoryReactor()
        self.protocol = MemCacheProtocol()
        self.transport = self.reactor.createTransport()
        self.protocol.makeConnection(self.transport)

    def test_initial_state(self):
        self.assertFalse(self.protocol._disconnected)
        self.assertEqual(self.protocol._current, deque())
        self.assertEqual(self.protocol.persistentTimeOut, 60)

    def test_sendLine_with_timeout(self):
        self.protocol.sendLine(b"set mykey 0 0 9")
        self.assertEqual(self.protocol.timeOut, 60)

    def test_connectionLost(self):
        self.protocol.connectionLost(None)
        self.assertTrue(self.protocol._disconnected)

    def test_cmd_ERROR(self):
        cmd = Command(b"invalid_command")
        self.protocol._current.append(cmd)
        self.protocol.cmd_ERROR()
        self.failureResultOf(cmd._deferred, NoSuchCommand)

    def test_cmd_CLIENT_ERROR(self):
        cmd = Command(b"client_error")
        self.protocol._current.append(cmd)
        self.protocol.cmd_CLIENT_ERROR(b"invalid input")
        self.failureResultOf(cmd._deferred, ClientError)

    def test_cmd_SERVER_ERROR(self):
        cmd = Command(b"server_error")
        self.protocol._current.append(cmd)
        self.protocol.cmd_SERVER_ERROR(b"server failure")
        self.failureResultOf(cmd._deferred, ServerError)

    def test_get_not_connected(self):
        d = self.protocol.get(b"key")
        self.failureResultOf(d, RuntimeError)

    def test_set_not_connected(self):
        d = self.protocol.set(b"key", b"value")
        self.failureResultOf(d, RuntimeError)

    def test_increment_not_connected(self):
        d = self.protocol.increment(b"key")
        self.failureResultOf(d, RuntimeError)

    def test_decrement_not_connected(self):
        d = self.protocol.decrement(b"key")
        self.failureResultOf(d, RuntimeError)

    def test_delete_not_connected(self):
        d = self.protocol.delete(b"key")
        self.failureResultOf(d, RuntimeError)

    def test_flushAll_not_connected(self):
        d = self.protocol.flushAll()
        self.failureResultOf(d, RuntimeError)

    def test_version_not_connected(self):
        d = self.protocol.version()
        self.failureResultOf(d, RuntimeError)


if __name__ == "__main__":
    unittest.main()