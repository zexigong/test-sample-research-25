# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

"""
Tests for L{twisted.test_address}.
"""

from twisted.trial.unittest import TestCase
from twisted.test_address import (
    UNIXAddress,
    IPv4Address,
    IPv6Address,
    HostnameAddress,
)


class TestIPv4Address(TestCase):
    """
    Tests for L{IPv4Address}.
    """

    def test_ipv4address(self):
        """
        Tests for the L{IPv4Address} class.
        """
        addr = IPv4Address("TCP", "127.0.0.1", 80)
        self.assertEqual(addr.type, "TCP")
        self.assertEqual(addr.host, "127.0.0.1")
        self.assertEqual(addr.port, 80)
        self.assertEqual(
            repr(addr), "IPv4Address(type='TCP', host='127.0.0.1', port=80)"
        )
        self.assertEqual(
            hash(addr), hash(("TCP", "127.0.0.1", 80))
        )  # Hash should be equal to a tuple


class TestIPv6Address(TestCase):
    """
    Tests for L{IPv6Address}.
    """

    def test_ipv6address(self):
        """
        Tests for the L{IPv6Address} class.
        """
        addr = IPv6Address("UDP", "::1", 80)
        self.assertEqual(addr.type, "UDP")
        self.assertEqual(addr.host, "::1")
        self.assertEqual(addr.port, 80)
        self.assertEqual(addr.flowInfo, 0)
        self.assertEqual(addr.scopeID, 0)
        self.assertEqual(
            repr(addr),
            "IPv6Address(type='UDP', host='::1', port=80, flowInfo=0, scopeID=0)",
        )
        self.assertEqual(
            hash(addr), hash(("UDP", "::1", 80, 0, 0))
        )  # Hash should be equal to a tuple


class TestUNIXAddress(TestCase):
    """
    Tests for L{UNIXAddress}.
    """

    def test_unixaddress(self):
        """
        Tests for the L{UNIXAddress} class.
        """
        addr = UNIXAddress(b"/path/to/socket")
        self.assertEqual(addr.name, b"/path/to/socket")
        self.assertEqual(repr(addr), "UNIXAddress('/path/to/socket')")
        self.assertEqual(hash(addr), hash(b"/path/to/socket"))


class TestHostnameAddress(TestCase):
    """
    Tests for L{HostnameAddress}.
    """

    def test_hostnameaddress(self):
        """
        Tests for the L{HostnameAddress} class.
        """
        addr = HostnameAddress(b"example.com", 80)
        self.assertEqual(addr.hostname, b"example.com")
        self.assertEqual(addr.port, 80)
        self.assertEqual(
            repr(addr), "HostnameAddress(hostname=b'example.com', port=80)"
        )
        self.assertEqual(
            hash(addr), hash((b"example.com", 80))
        )  # Hash should be equal to a tuple