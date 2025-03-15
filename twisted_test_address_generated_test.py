# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

"""
Tests for L{twisted.internet.address}.
"""

import os

from twisted.python.compat import nativeString
from twisted.trial.unittest import SynchronousTestCase

from twisted.internet.address import (
    IPv4Address,
    IPv6Address,
    UNIXAddress,
    HostnameAddress,
    _ServerFactoryIPv4Address,
)


class IPv4AddressTests(SynchronousTestCase):
    """
    Tests for L{IPv4Address}.
    """

    def test_equal(self):
        """
        Two L{IPv4Address} instances with equal attributes compare equal.
        """
        a = IPv4Address("TCP", "192.168.1.2", 1234)
        b = IPv4Address("TCP", "192.168.1.2", 1234)
        self.assertEqual(a, b)

    def test_notEqual(self):
        """
        Two L{IPv4Address} instances with differing attributes compare
        not equal.
        """
        a = IPv4Address("TCP", "192.168.1.2", 1234)
        b = IPv4Address("TCP", "192.168.1.2", 1235)
        self.assertNotEqual(a, b)

    def test_hash(self):
        """
        Two equal L{IPv4Address} instances produce the same hash value.
        """
        a = IPv4Address("TCP", "192.168.1.2", 1234)
        b = IPv4Address("TCP", "192.168.1.2", 1234)
        self.assertEqual(hash(a), hash(b))

    def test_repr(self):
        """
        L{IPv4Address.__repr__} returns a string representation of an
        L{IPv4Address} instance that includes the type, host, and port.
        """
        self.assertEqual(
            repr(IPv4Address("TCP", "192.168.1.2", 1234)),
            "IPv4Address(type='TCP', host='192.168.1.2', port=1234)",
        )

    def test_serverFactoryBackwardCompatibility(self):
        """
        L{_ServerFactoryIPv4Address} instances compare equal to two-tuples of
        the host and port, to preserve backwards compatibility with
        L{twisted.internet.protocol.ServerFactory} implementations that
        override L{twisted.internet.protocol.ServerFactory.buildProtocol} and
        expect a two-tuple of the host and port to be passed in.
        """
        a = _ServerFactoryIPv4Address("TCP", "192.168.1.2", 1234)
        b = ("192.168.1.2", 1234)
        self.assertEqual(a, b)

    def test_serverFactoryBackwardCompatibilityWithWarning(self):
        """
        L{_ServerFactoryIPv4Address} instances compare equal to two-tuples of
        the host and port with a L{DeprecationWarning} issued, to preserve
        backwards compatibility with L{twisted.internet.protocol.ServerFactory}
        implementations that override L{twisted.internet.protocol.ServerFactory.buildProtocol}
        and expect a two-tuple of the host and port to be passed in.
        """
        a = _ServerFactoryIPv4Address("TCP", "192.168.1.2", 1234)
        b = ("192.168.1.2", 1234)

        def _deprecated():
            self.assertEqual(a, b)

        warnings = self.assertWarns(
            DeprecationWarning,
            _deprecated,
            "IPv4Address.__getitem__ is deprecated.  Use attributes instead.",
        )

        self.assertEqual(len(warnings), 1)

    def test_serverFactoryBackwardCompatibilityNotEqual(self):
        """
        L{_ServerFactoryIPv4Address} instances do not compare equal to
        two-tuples of the host and port if the host or port are different.
        """
        a = _ServerFactoryIPv4Address("TCP", "192.168.1.2", 1234)
        b = ("192.168.1.2", 1235)
        self.assertNotEqual(a, b)

    def test_serverFactoryBackwardCompatibilityNotEqualWithWarning(self):
        """
        L{_ServerFactoryIPv4Address} instances do not compare equal to
        two-tuples of the host and port if the host or port are different.
        """
        a = _ServerFactoryIPv4Address("TCP", "192.168.1.2", 1234)
        b = ("192.168.1.2", 1235)

        def _deprecated():
            self.assertNotEqual(a, b)

        warnings = self.assertWarns(
            DeprecationWarning,
            _deprecated,
            "IPv4Address.__getitem__ is deprecated.  Use attributes instead.",
        )

        self.assertEqual(len(warnings), 1)


class IPv6AddressTests(SynchronousTestCase):
    """
    Tests for L{IPv6Address}.
    """

    def test_equal(self):
        """
        Two L{IPv6Address} instances with equal attributes compare equal.
        """
        a = IPv6Address("TCP", "::1", 1234)
        b = IPv6Address("TCP", "::1", 1234)
        self.assertEqual(a, b)

    def test_notEqual(self):
        """
        Two L{IPv6Address} instances with differing attributes compare
        not equal.
        """
        a = IPv6Address("TCP", "::1", 1234)
        b = IPv6Address("TCP", "::1", 1235)
        self.assertNotEqual(a, b)

    def test_hash(self):
        """
        Two equal L{IPv6Address} instances produce the same hash value.
        """
        a = IPv6Address("TCP", "::1", 1234)
        b = IPv6Address("TCP", "::1", 1234)
        self.assertEqual(hash(a), hash(b))

    def test_repr(self):
        """
        L{IPv6Address.__repr__} returns a string representation of an
        L{IPv6Address} instance that includes the type, host, and port.
        """
        self.assertEqual(
            repr(IPv6Address("TCP", "::1", 1234)),
            "IPv6Address(type='TCP', host='::1', port=1234, flowInfo=0, scopeID=0)",
        )


class UNIXAddressTests(SynchronousTestCase):
    """
    Tests for L{UNIXAddress}.
    """

    def test_equal(self):
        """
        Two L{UNIXAddress} instances with equal attributes compare equal.
        """
        a = UNIXAddress(nativeString(b"/var/foo"))
        b = UNIXAddress(nativeString(b"/var/foo"))
        self.assertEqual(a, b)

    def test_notEqual(self):
        """
        Two L{UNIXAddress} instances with differing attributes compare
        not equal.
        """
        a = UNIXAddress(nativeString(b"/var/foo"))
        b = UNIXAddress(nativeString(b"/var/bar"))
        self.assertNotEqual(a, b)

    def test_hash(self):
        """
        Two equal L{UNIXAddress} instances produce the same hash value.
        """
        a = UNIXAddress(nativeString(b"/var/foo"))
        b = UNIXAddress(nativeString(b"/var/foo"))
        self.assertEqual(hash(a), hash(b))

    def test_repr(self):
        """
        L{UNIXAddress.__repr__} returns a string representation of an
        L{UNIXAddress} instance that includes the name.
        """
        self.assertEqual(
            repr(UNIXAddress(nativeString(b"/var/foo"))), "UNIXAddress('/var/foo')"
        )

    def test_unhashable(self):
        """
        L{UNIXAddress} instances with abstract namespace addresses are
        not hashable.
        """
        self.assertRaises(TypeError, hash, UNIXAddress(nativeString(b"\x00foo")))


class HostnameAddressTests(SynchronousTestCase):
    """
    Tests for L{HostnameAddress}.
    """

    def test_equal(self):
        """
        Two L{HostnameAddress} instances with equal attributes compare equal.
        """
        a = HostnameAddress(b"example.com", 1234)
        b = HostnameAddress(b"example.com", 1234)
        self.assertEqual(a, b)

    def test_notEqual(self):
        """
        Two L{HostnameAddress} instances with differing attributes compare
        not equal.
        """
        a = HostnameAddress(b"example.com", 1234)
        b = HostnameAddress(b"example.com", 1235)
        self.assertNotEqual(a, b)

    def test_hash(self):
        """
        Two equal L{HostnameAddress} instances produce the same hash value.
        """
        a = HostnameAddress(b"example.com", 1234)
        b = HostnameAddress(b"example.com", 1234)
        self.assertEqual(hash(a), hash(b))

    def test_repr(self):
        """
        L{HostnameAddress.__repr__} returns a string representation of an
        L{HostnameAddress} instance that includes the hostname and port.
        """
        self.assertEqual(
            repr(HostnameAddress(b"example.com", 1234)),
            "HostnameAddress(hostname='example.com', port=1234)",
        )