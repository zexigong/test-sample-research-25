import pytest
from unittest.mock import MagicMock
from twisted.protocols.basic import LineReceiver
from twisted.test.proto_helpers import StringTransport

from twisted.test_finger.finger import Finger


class TestFingerProtocol:
    def setup_method(self):
        self.protocol = Finger()
        self.transport = StringTransport()
        self.protocol.makeConnection(self.transport)

    def test_lineReceived_empty(self):
        self.protocol.lineReceived(b"")
        assert self.transport.value() == b"Finger online list denied\n"
        assert self.transport.disconnecting

    def test_lineReceived_user(self):
        self.protocol.lineReceived(b"user")
        assert self.transport.value() == b"Login: user\nNo such user\n"
        assert self.transport.disconnecting

    def test_lineReceived_user_with_slash_w(self):
        self.protocol.lineReceived(b"/W user")
        assert self.transport.value() == b"Login: user\nNo such user\n"
        assert self.transport.disconnecting

    def test_lineReceived_domain(self):
        self.protocol.lineReceived(b"@domain")
        assert self.transport.value() == b"Finger forwarding service denied\n"
        assert self.transport.disconnecting

    def test_lineReceived_user_at_domain(self):
        self.protocol.lineReceived(b"user@domain")
        assert self.transport.value() == b"Finger forwarding service denied\n"
        assert self.transport.disconnecting

    def test_refuseMessage(self):
        message = b"Test message"
        self.protocol._refuseMessage(message)
        assert self.transport.value() == b"Test message\n"
        assert self.transport.disconnecting

    def test_forwardQuery(self):
        self.protocol.forwardQuery(0, b"user", b"domain")
        assert self.transport.value() == b"Finger forwarding service denied\n"
        assert self.transport.disconnecting

    def test_getDomain(self):
        self.protocol.getDomain(0)
        assert self.transport.value() == b"Finger online list denied\n"
        assert self.transport.disconnecting

    def test_getUser(self):
        self.protocol.getUser(0, b"user")
        assert self.transport.value() == b"Login: user\nNo such user\n"
        assert self.transport.disconnecting

if __name__ == "__main__":
    pytest.main()