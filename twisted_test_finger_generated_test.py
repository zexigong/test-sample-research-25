# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

"""
Tests for L{twisted.protocols.finger}.
"""

from twisted.internet import reactor, protocol, defer
from twisted.protocols import finger
from twisted.test import proto_helpers


class FingerTests(protocol.Protocol):
    """
    A L{Finger} protocol implementation with a known response.

    @ivar response: The response that will be returned to the client.
    @type response: L{bytes}
    """

    response = None

    def lineReceived(self, line):
        """
        Handle a request by writing a response to the transport.
        """
        self.transport.write(self.response)
        self.transport.loseConnection()


class UserFingerTests(FingerTests):
    """
    A L{Finger} protocol implementation with a known response to a
    user request.
    """

    response = b"Login: alice\nNo such user\n"


class DomainFingerTests(FingerTests):
    """
    A L{Finger} protocol implementation with a known response to a
    domain request.
    """

    response = b"Finger online list denied\n"


class ForwardFingerTests(FingerTests):
    """
    A L{Finger} protocol implementation with a known response to a
    forward request.
    """

    response = b"Finger forwarding service denied\n"


class FingerServerTests(protocol.ServerFactory):
    """
    A L{ServerFactory} that builds the L{Finger} protocol.
    """

    protocol = finger.Finger

    def buildProtocol(self, addr):
        """
        Create a new L{Finger} protocol.
        """
        return self.protocol()


class UserFingerServerTests(FingerServerTests):
    """
    A L{ServerFactory} that builds the L{UserFinger} protocol.
    """

    protocol = UserFingerTests


class DomainFingerServerTests(FingerServerTests):
    """
    A L{ServerFactory} that builds the L{DomainFinger} protocol.
    """

    protocol = DomainFingerTests


class ForwardFingerServerTests(FingerServerTests):
    """
    A L{ServerFactory} that builds the L{ForwardFinger} protocol.
    """

    protocol = ForwardFingerTests


class FingerClientTests(protocol.Protocol):
    """
    A L{Finger} client implementation that will send a request and
    receive a response.

    @ivar deferred: The L{Deferred} that will receive the response.
    @type deferred: L{Deferred}
    """

    def __init__(self, deferred):
        """
        Initialize the L{Finger} client.

        @param deferred: The L{Deferred} that will receive the response.
        @type deferred: L{Deferred}
        """
        self.deferred = deferred

    def connectionMade(self):
        """
        Send a request to the server.
        """
        self.transport.write(b"alice\n")

    def dataReceived(self, data):
        """
        Pass the response to the L{Deferred}.
        """
        self.deferred.callback(data)


class UserFingerClientTests(FingerClientTests):
    """
    A L{Finger} client implementation that will send a user request
    and receive a response.
    """


class DomainFingerClientTests(FingerClientTests):
    """
    A L{Finger} client implementation that will send a domain request
    and receive a response.
    """

    def connectionMade(self):
        """
        Send a request to the server.
        """
        self.transport.write(b"\n")


class ForwardFingerClientTests(FingerClientTests):
    """
    A L{Finger} client implementation that will send a forward request
    and receive a response.
    """

    def connectionMade(self):
        """
        Send a request to the server.
        """
        self.transport.write(b"alice@alice.com\n")


class FingerClientFactoryTests(protocol.ClientFactory):
    """
    A L{ClientFactory} that builds the L{FingerClient} protocol.
    """

    protocol = FingerClientTests

    def __init__(self, deferred):
        """
        Initialize the L{FingerClientFactory}.

        @param deferred: The L{Deferred} that will receive the response.
        @type deferred: L{Deferred}
        """
        self.deferred = deferred

    def buildProtocol(self, addr):
        """
        Create a new L{FingerClient} protocol.
        """
        return self.protocol(self.deferred)


class UserFingerClientFactoryTests(FingerClientFactoryTests):
    """
    A L{ClientFactory} that builds the L{UserFingerClient} protocol.
    """

    protocol = UserFingerClientTests


class DomainFingerClientFactoryTests(FingerClientFactoryTests):
    """
    A L{ClientFactory} that builds the L{DomainFingerClient} protocol.
    """

    protocol = DomainFingerClientTests


class ForwardFingerClientFactoryTests(FingerClientFactoryTests):
    """
    A L{ClientFactory} that builds the L{ForwardFingerClient} protocol.
    """

    protocol = ForwardFingerClientTests


class FingerTestCaseTests(protocol.ServerFactory):
    """
    A test case for the L{Finger} protocol.
    """

    def setUp(self):
        """
        Initialize the L{FingerTestCase}.
        """
        self.server = reactor.listenTCP(0, self.serverFactory, interface="127.0.0.1")
        self.port = self.server.getHost().port

    def tearDown(self):
        """
        Clean up the L{FingerTestCase}.
        """
        return self.server.stopListening()


class UserFingerTestCaseTests(FingerTestCaseTests):
    """
    A test case for the L{UserFinger} protocol.
    """

    serverFactory = UserFingerServerTests

    def testRequest(self):
        """
        Test a request to the L{UserFinger} server.
        """
        d = defer.Deferred()
        clientFactory = UserFingerClientFactoryTests(d)
        reactor.connectTCP("127.0.0.1", self.port, clientFactory)
        return d.addCallback(self.assertEqual, b"Login: alice\nNo such user\n")


class DomainFingerTestCaseTests(FingerTestCaseTests):
    """
    A test case for the L{DomainFinger} protocol.
    """

    serverFactory = DomainFingerServerTests

    def testRequest(self):
        """
        Test a request to the L{DomainFinger} server.
        """
        d = defer.Deferred()
        clientFactory = DomainFingerClientFactoryTests(d)
        reactor.connectTCP("127.0.0.1", self.port, clientFactory)
        return d.addCallback(self.assertEqual, b"Finger online list denied\n")


class ForwardFingerTestCaseTests(FingerTestCaseTests):
    """
    A test case for the L{ForwardFinger} protocol.
    """

    serverFactory = ForwardFingerServerTests

    def testRequest(self):
        """
        Test a request to the L{ForwardFinger} server.
        """
        d = defer.Deferred()
        clientFactory = ForwardFingerClientFactoryTests(d)
        reactor.connectTCP("127.0.0.1", self.port, clientFactory)
        return d.addCallback(self.assertEqual, b"Finger forwarding service denied\n")