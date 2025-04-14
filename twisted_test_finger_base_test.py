# test_finger.py
from twisted.trial import unittest
from twisted.test.proto_helpers import StringTransport
from twisted.protocols.basic import LineReceiver
from twisted.test import proto_helpers
from twisted.protocols import basic
from twisted.internet import error

class TestFingerProtocol(unittest.TestCase):
    def setUp(self):
        self.transport = proto_helpers.StringTransport()
        self.protocol = Finger()
        self.protocol.makeConnection(self.transport)

    def test_lineReceived_empty(self):
        self.protocol.lineReceived(b"")
        self.assertEqual(self.transport.value(), b"Finger online list denied\n")
        self.assertTrue(self.transport.disconnecting)

    def test_lineReceived_user(self):
        self.protocol.lineReceived(b"user")
        self.assertEqual(self.transport.value(), b"Login: user\nNo such user\n")
        self.assertTrue(self.transport.disconnecting)

    def test_lineReceived_user_with_host(self):
        self.protocol.lineReceived(b"user@host")
        self.assertEqual(self.transport.value(), b"Finger forwarding service denied\n")
        self.assertTrue(self.transport.disconnecting)

    def test_lineReceived_slash_w_user(self):
        self.protocol.lineReceived(b"/W user")
        self.assertEqual(self.transport.value(), b"Login: user\nNo such user\n")
        self.assertTrue(self.transport.disconnecting)

    def test_lineReceived_slash_w_user_with_host(self):
        self.protocol.lineReceived(b"/W user@host")
        self.assertEqual(self.transport.value(), b"Finger forwarding service denied\n")
        self.assertTrue(self.transport.disconnecting)

    def test_lineReceived_slash_w_empty(self):
        self.protocol.lineReceived(b"/W")
        self.assertEqual(self.transport.value(), b"Finger online list denied\n")
        self.assertTrue(self.transport.disconnecting)

class Finger(basic.LineReceiver):
    def lineReceived(self, line):
        parts = line.split()
        if not parts:
            parts = [b""]
        if len(parts) == 1:
            slash_w = 0
        else:
            slash_w = 1
        user = parts[-1]
        if b"@" in user:
            hostPlace = user.rfind(b"@")
            user = user[:hostPlace]
            host = user[hostPlace + 1 :]
            return self.forwardQuery(slash_w, user, host)
        if user:
            return self.getUser(slash_w, user)
        else:
            return self.getDomain(slash_w)

    def _refuseMessage(self, message):
        self.transport.write(message + b"\n")
        self.transport.loseConnection()

    def forwardQuery(self, slash_w, user, host):
        self._refuseMessage(b"Finger forwarding service denied")

    def getDomain(self, slash_w):
        self._refuseMessage(b"Finger online list denied")

    def getUser(self, slash_w, user):
        self.transport.write(b"Login: " + user + b"\n")
        self._refuseMessage(b"No such user")