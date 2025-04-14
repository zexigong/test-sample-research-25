from twisted.trial import unittest
from twisted.test_address.test_address import (
    IPv4Address,
    IPv6Address,
    UNIXAddress,
    HostnameAddress,
    _ServerFactoryIPv4Address,
)
from twisted.internet.interfaces import IAddress
from zope.interface.verify import verifyClass, verifyObject


class IPv4AddressTests(unittest.TestCase):
    def test_ipv4_address_creation(self):
        addr = IPv4Address(type="TCP", host="127.0.0.1", port=80)
        self.assertEqual(addr.type, "TCP")
        self.assertEqual(addr.host, "127.0.0.1")
        self.assertEqual(addr.port, 80)

    def test_ipv4_address_invalid_type(self):
        with self.assertRaises(ValueError):
            IPv4Address(type="FTP", host="127.0.0.1", port=80)

    def test_ipv4_address_implements_iaddress(self):
        self.assertTrue(verifyClass(IAddress, IPv4Address))
        self.assertTrue(verifyObject(IAddress, IPv4Address(type="TCP", host="127.0.0.1", port=80)))


class IPv6AddressTests(unittest.TestCase):
    def test_ipv6_address_creation(self):
        addr = IPv6Address(type="UDP", host="::1", port=8080)
        self.assertEqual(addr.type, "UDP")
        self.assertEqual(addr.host, "::1")
        self.assertEqual(addr.port, 8080)
        self.assertEqual(addr.flowInfo, 0)
        self.assertEqual(addr.scopeID, 0)

    def test_ipv6_address_invalid_type(self):
        with self.assertRaises(ValueError):
            IPv6Address(type="ICMP", host="::1", port=8080)

    def test_ipv6_address_implements_iaddress(self):
        self.assertTrue(verifyClass(IAddress, IPv6Address))
        self.assertTrue(verifyObject(IAddress, IPv6Address(type="UDP", host="::1", port=8080)))


class UNIXAddressTests(unittest.TestCase):
    def test_unix_address_creation(self):
        addr = UNIXAddress(name=b"/tmp/socket")
        self.assertEqual(addr.name, b"/tmp/socket")

    def test_unix_address_implements_iaddress(self):
        self.assertTrue(verifyClass(IAddress, UNIXAddress))
        self.assertTrue(verifyObject(IAddress, UNIXAddress(name=b"/tmp/socket")))

    def test_unix_address_equality(self):
        addr1 = UNIXAddress(name=b"/tmp/socket1")
        addr2 = UNIXAddress(name=b"/tmp/socket1")
        addr3 = UNIXAddress(name=b"/tmp/socket2")
        self.assertEqual(addr1, addr2)
        self.assertNotEqual(addr1, addr3)


class HostnameAddressTests(unittest.TestCase):
    def test_hostname_address_creation(self):
        addr = HostnameAddress(hostname=b"example.com", port=443)
        self.assertEqual(addr.hostname, b"example.com")
        self.assertEqual(addr.port, 443)

    def test_hostname_address_implements_iaddress(self):
        self.assertTrue(verifyClass(IAddress, HostnameAddress))
        self.assertTrue(verifyObject(IAddress, HostnameAddress(hostname=b"example.com", port=443)))


class ServerFactoryIPv4AddressTests(unittest.TestCase):
    def test_server_factory_ipv4_address_equality(self):
        addr1 = _ServerFactoryIPv4Address(type="TCP", host="127.0.0.1", port=8080)
        addr2 = _ServerFactoryIPv4Address(type="TCP", host="127.0.0.1", port=8080)
        addr3 = _ServerFactoryIPv4Address(type="UDP", host="127.0.0.1", port=8080)
        self.assertEqual(addr1, addr2)
        self.assertNotEqual(addr1, addr3)

    def test_server_factory_ipv4_address_tuple_equality(self):
        addr = _ServerFactoryIPv4Address(type="TCP", host="127.0.0.1", port=8080)
        self.assertEqual(addr, ("127.0.0.1", 8080))