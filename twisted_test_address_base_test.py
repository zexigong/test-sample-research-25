import pytest
from twisted.test_address.test_address import (
    IPv4Address,
    IPv6Address,
    HostnameAddress,
    UNIXAddress,
    _ServerFactoryIPv4Address,
)
import os

def test_ipv4_address_creation():
    addr = IPv4Address(type="TCP", host="127.0.0.1", port=8080)
    assert addr.type == "TCP"
    assert addr.host == "127.0.0.1"
    assert addr.port == 8080

    addr_udp = IPv4Address(type="UDP", host="192.168.1.1", port=53)
    assert addr_udp.type == "UDP"
    assert addr_udp.host == "192.168.1.1"
    assert addr_udp.port == 53

def test_ipv6_address_creation():
    addr = IPv6Address(type="TCP", host="::1", port=8080)
    assert addr.type == "TCP"
    assert addr.host == "::1"
    assert addr.port == 8080
    assert addr.flowInfo == 0
    assert addr.scopeID == 0

    addr_custom = IPv6Address(type="UDP", host="2001:db8::1", port=53, flowInfo=1, scopeID="eth0")
    assert addr_custom.type == "UDP"
    assert addr_custom.host == "2001:db8::1"
    assert addr_custom.port == 53
    assert addr_custom.flowInfo == 1
    assert addr_custom.scopeID == "eth0"

def test_hostname_address_creation():
    addr = HostnameAddress(hostname=b"example.com", port=80)
    assert addr.hostname == b"example.com"
    assert addr.port == 80

def test_unix_address_creation():
    addr = UNIXAddress(name=b"/tmp/socket")
    assert addr.name == b"/tmp/socket"

    addr_none = UNIXAddress()
    assert addr_none.name is None

def test_unix_address_equality():
    addr1 = UNIXAddress(name=b"/tmp/socket1")
    addr2 = UNIXAddress(name=b"/tmp/socket2")

    assert addr1 != addr2

    addr3 = UNIXAddress(name=b"/tmp/socket1")
    assert addr1 == addr3

def test_unix_address_repr():
    addr = UNIXAddress(name=b"/tmp/socket")
    assert repr(addr) == "UNIXAddress('/tmp/socket')"

def test_unix_address_hash():
    addr = UNIXAddress(name=b"/tmp/socket")
    try:
        os.stat(addr.name)
        assert isinstance(hash(addr), int)
    except OSError:
        assert hash(addr) == hash(b"/tmp/socket")

def test_server_factory_ipv4_address_equality():
    addr1 = _ServerFactoryIPv4Address(type="TCP", host="127.0.0.1", port=8080)
    addr2 = _ServerFactoryIPv4Address(type="TCP", host="127.0.0.1", port=8080)
    addr3 = _ServerFactoryIPv4Address(type="TCP", host="192.168.1.1", port=8080)

    assert addr1 == addr2
    assert addr1 != addr3

    assert addr1 == ("127.0.0.1", 8080)