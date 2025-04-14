# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

from twisted.test.proto_helpers import StringTransportWithDisconnection
from twisted.trial import unittest

from twisted.protocols import finger


class TestFinger(unittest.TestCase):
    def setUp(self):
        self.protocol = finger.Finger()
        self.transport = StringTransportWithDisconnection()
        self.protocol.makeConnection(self.transport)

    def tearDown(self):
        self.transport.clear()

    def test_empty(self):
        self.protocol.lineReceived(b"")
        self.assertEqual(
            self.transport.value(), b"Finger online list denied\n"
        )
        self.assertTrue(self.transport.disconnecting)

    def test_w(self):
        self.protocol.lineReceived(b"/W")
        self.assertEqual(
            self.transport.value(), b"Finger online list denied\n"
        )
        self.assertTrue(self.transport.disconnecting)

    def test_user(self):
        self.protocol.lineReceived(b"foo")
        self.assertEqual(self.transport.value(), b"Login: foo\nNo such user\n")
        self.assertTrue(self.transport.disconnecting)

    def test_user_w(self):
        self.protocol.lineReceived(b"/W foo")
        self.assertEqual(self.transport.value(), b"Login: foo\nNo such user\n")
        self.assertTrue(self.transport.disconnecting)

    def test_forwarding(self):
        self.protocol.lineReceived(b"foo@example.com")
        self.assertEqual(
            self.transport.value(), b"Finger forwarding service denied\n"
        )
        self.assertTrue(self.transport.disconnecting)

    def test_forwarding_w(self):
        self.protocol.lineReceived(b"/W foo@example.com")
        self.assertEqual(
            self.transport.value(), b"Finger forwarding service denied\n"
        )
        self.assertTrue(self.transport.disconnecting)

    def test_host(self):
        self.protocol.lineReceived(b"@example.com")
        self.assertEqual(
            self.transport.value(), b"Finger forwarding service denied\n"
        )
        self.assertTrue(self.transport.disconnecting)

    def test_host_w(self):
        self.protocol.lineReceived(b"/W @example.com")
        self.assertEqual(
            self.transport.value(), b"Finger forwarding service denied\n"
        )
        self.assertTrue(self.transport.disconnecting)