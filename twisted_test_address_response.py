# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

"""
Test cases for L{twisted.internet.address} module.
"""

from twisted.trial.unittest import SynchronousTestCase
from twisted.internet.address import (
    IPv4Address,
    IPv6Address,
    UNIXAddress,
    HostnameAddress,
    _ServerFactoryIPv4Address,
)
from twisted.python.runtime import platform


class HostnameAddressTests(SynchronousTestCase):
    """
    Tests for L{HostnameAddress}.
    """

    def test_hash(self) -> None:
        """
        L{HostnameAddress} can be used as a key in a dictionary.
        """
        a = HostnameAddress(b"example.com", 80)
        b = HostnameAddress(b"example.com", 80)
        c = HostnameAddress(b"another.com", 80)
        self.assertEqual(hash(a), hash(b))
        self.assertNotEqual(hash(a), hash(c))

    def test_equality(self) -> None:
        """
        L{HostnameAddress} compares equal to other L{HostnameAddress} instances
        with the same host and port values.
        """
        a = HostnameAddress(b"example.com", 80)
        b = HostnameAddress(b"example.com", 80)
        c = HostnameAddress(b"another.com", 80)
        self.assertEqual(a, b)
        self.assertNotEqual(a, c)


class IPv4AddressTests(SynchronousTestCase):
    """
    Tests for L{IPv4Address}.
    """

    def test_hash(self) -> None:
        """
        L{IPv4Address} can be used as a key in a dictionary.
        """
        a = IPv4Address("TCP", "127.0.0.1", 80)
        b = IPv4Address("TCP", "127.0.0.1", 80)
        c = IPv4Address("UDP", "127.0.0.1", 80)
        d = IPv4Address("TCP", "127.0.0.1", 88)
        e = IPv4Address("TCP", "127.0.0.2", 80)
        self.assertEqual(hash(a), hash(b))
        self.assertNotEqual(hash(a), hash(c))
        self.assertNotEqual(hash(a), hash(d))
        self.assertNotEqual(hash(a), hash(e))

    def test_equality(self) -> None:
        """
        L{IPv4Address} compares equal to other L{IPv4Address} instances with
        the same type, host, and port values.
        """
        a = IPv4Address("TCP", "127.0.0.1", 80)
        b = IPv4Address("TCP", "127.0.0.1", 80)
        c = IPv4Address("UDP", "127.0.0.1", 80)
        d = IPv4Address("TCP", "127.0.0.1", 88)
        e = IPv4Address("TCP", "127.0.0.2", 80)
        self.assertEqual(a, b)
        self.assertNotEqual(a, c)
        self.assertNotEqual(a, d)
        self.assertNotEqual(a, e)


class IPv6AddressTests(SynchronousTestCase):
    """
    Tests for L{IPv6Address}.
    """

    def test_hash(self) -> None:
        """
        L{IPv6Address} can be used as a key in a dictionary.
        """
        a = IPv6Address("TCP", "::1", 80)
        b = IPv6Address("TCP", "::1", 80)
        c = IPv6Address("UDP", "::1", 80)
        d = IPv6Address("TCP", "::1", 88)
        e = IPv6Address("TCP", "::2", 80)
        self.assertEqual(hash(a), hash(b))
        self.assertNotEqual(hash(a), hash(c))
        self.assertNotEqual(hash(a), hash(d))
        self.assertNotEqual(hash(a), hash(e))

    def test_equality(self) -> None:
        """
        L{IPv6Address} compares equal to other L{IPv6Address} instances with
        the same type, host, port, flowInfo, and scopeID values.
        """
        a = IPv6Address("TCP", "::1", 80)
        b = IPv6Address("TCP", "::1", 80)
        c = IPv6Address("UDP", "::1", 80)
        d = IPv6Address("TCP", "::1", 88)
        e = IPv6Address("TCP", "::2", 80)
        self.assertEqual(a, b)
        self.assertNotEqual(a, c)
        self.assertNotEqual(a, d)
        self.assertNotEqual(a, e)

    def test_equalityFlowInfo(self) -> None:
        """
        L{IPv6Address} compares equal to other L{IPv6Address} instances with
        the same type, host, port, flowInfo, and scopeID values.
        """
        a = IPv6Address("TCP", "::1", 80, flowInfo=1)
        b = IPv6Address("TCP", "::1", 80, flowInfo=1)
        c = IPv6Address("TCP", "::1", 80, flowInfo=2)
        self.assertEqual(a, b)
        self.assertNotEqual(a, c)

    def test_equalityScopeID(self) -> None:
        """
        L{IPv6Address} compares equal to other L{IPv6Address} instances with
        the same type, host, port, flowInfo, and scopeID values.
        """
        a = IPv6Address("TCP", "::1", 80, scopeID=1)
        b = IPv6Address("TCP", "::1", 80, scopeID=1)
        c = IPv6Address("TCP", "::1", 80, scopeID=2)
        self.assertEqual(a, b)
        self.assertNotEqual(a, c)


class UNIXAddressTests(SynchronousTestCase):
    """
    Tests for L{UNIXAddress}.
    """

    def test_hash(self) -> None:
        """
        L{UNIXAddress} can be used as a key in a dictionary.
        """
        a = UNIXAddress(b"/var/run/socket")
        b = UNIXAddress(b"/var/run/socket")
        c = UNIXAddress(b"/var/run/other")
        d = UNIXAddress(None)
        e = UNIXAddress(None)
        self.assertEqual(hash(a), hash(b))
        self.assertNotEqual(hash(a), hash(c))
        self.assertEqual(hash(d), hash(e))

    def test_equality(self) -> None:
        """
        L{UNIXAddress} compares equal to other L{UNIXAddress} instances with
        the same name values.
        """
        a = UNIXAddress(b"/var/run/socket")
        b = UNIXAddress(b"/var/run/socket")
        c = UNIXAddress(b"/var/run/other")
        d = UNIXAddress(None)
        e = UNIXAddress(None)
        self.assertEqual(a, b)
        self.assertNotEqual(a, c)
        self.assertEqual(d, e)

    def test_samefile(self) -> None:
        """
        L{UNIXAddress} compares equal to other L{UNIXAddress} instances with
        names that point to the same file, if the platform supports
        L{os.path.samefile}.
        """
        if getattr(os.path, "samefile", None) is None:
            raise self.skipTest(
                "Platform does not support os.path.samefile, cannot run test."
            )
        tmp = self.mktemp()
        a = UNIXAddress(tmp)
        b = UNIXAddress(tmp)
        c = UNIXAddress(tmp + ".other")
        with open(tmp, "w"):
            pass
        os.link(tmp, tmp + ".other")
        self.assertEqual(a, b)
        self.assertEqual(a, c)

    def test_samefileAbstractNamespace(self) -> None:
        """
        L{UNIXAddress} compares equal to other L{UNIXAddress} instances with
        names that point to the same abstract namespace UNIX socket, if the
        platform supports L{os.path.samefile}. Abstract namespace UNIX sockets
        are supported on Linux only.
        """
        if not platform.isLinux():
            raise self.skipTest(
                "Platform does not support abstract namespace UNIX sockets, "
                "cannot run test."
            )
        a = UNIXAddress(b"\0foo")
        b = UNIXAddress(b"\0foo")
        c = UNIXAddress(b"\0bar")
        self.assertEqual(a, b)
        self.assertNotEqual(a, c)

    def test_repr(self) -> None:
        """
        L{repr} of L{UNIXAddress} uses the L{name} attribute.
        """
        a = UNIXAddress(b"/var/run/socket")
        self.assertEqual(repr(a), "UNIXAddress('/var/run/socket')")
        a = UNIXAddress(None)
        self.assertEqual(repr(a), "UNIXAddress(None)")


class _ServerFactoryIPv4AddressTests(SynchronousTestCase):
    """
    Tests for L{_ServerFactoryIPv4Address}.
    """

    def test_deprecated(self) -> None:
        """
        L{_ServerFactoryIPv4Address.__eq__} with a L{tuple} issues a
        L{DeprecationWarning}.
        """
        a = _ServerFactoryIPv4Address("TCP", "127.0.0.1", 80)
        b = ("127.0.0.1", 80)
        self.assertWarns(
            DeprecationWarning,
            "IPv4Address.__getitem__ is deprecated.  Use attributes instead.",
            __file__,
            lambda: self.assertEqual(a, b),
        )