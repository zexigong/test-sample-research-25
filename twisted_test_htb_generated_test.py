# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

"""
Tests for L{twisted.protocols.htb}.
"""

from time import time, sleep
from unittest import TestCase

from zope.interface import implementer

from twisted.internet import interfaces
from twisted.internet.defer import Deferred, DeferredList
from twisted.internet.task import Clock
from twisted.protocols import htb


class BucketTests(TestCase):
    """
    Tests for L{htb.Bucket}.
    """

    def setUp(self):
        """
        Set up a bucket with a maxburst of 100, and a rate of 50.
        """
        self.b1 = htb.Bucket()
        self.b1.maxburst = 100
        self.b1.rate = 50
        self.start = time()

    def test_add(self):
        """
        Test that we can add tokens to a bucket.
        """
        self.b1.add(60)
        self.assertEqual(self.b1.content, 60)

    def test_addTooManyTokens(self):
        """
        Test that we cannot add more tokens to a bucket than it can handle.
        """
        self.b1.add(60)
        self.b1.add(60)
        self.assertEqual(self.b1.content, 100)

    def test_addNegativeTokens(self):
        """
        Test that adding negative tokens does not change the bucket's content.
        """
        self.b1.add(-10)
        self.assertEqual(self.b1.content, 0)

    def test_addMoreThanMaxburst(self):
        """
        Test that we cannot add more tokens to a bucket than its maxburst.
        """
        self.b1.add(1000)
        self.assertEqual(self.b1.content, 100)

    def test_fillParentToo(self):
        """
        Test that adding tokens to a bucket with a parent also fills the
        parent bucket.
        """
        b2 = htb.Bucket(self.b1)
        b2.maxburst = 200
        b2.rate = 100
        b2.add(60)
        self.assertEqual(b2.content, 60)
        self.assertEqual(self.b1.content, 60)

    def test_fillParentTooFull(self):
        """
        Test that adding tokens to a bucket with a parent also fills the
        parent bucket, but will not overfill it.
        """
        b2 = htb.Bucket(self.b1)
        b2.maxburst = 200
        b2.rate = 100
        b2.add(160)
        self.assertEqual(b2.content, 100)
        self.assertEqual(self.b1.content, 100)

    def test_fillParentTooFullToAChildsMaxburst(self):
        """
        Test that adding tokens to a bucket with a parent also fills the
        parent bucket, but will not overfill it.
        """
        b2 = htb.Bucket(self.b1)
        b2.maxburst = 60
        b2.rate = 100
        b2.add(160)
        self.assertEqual(b2.content, 60)
        self.assertEqual(self.b1.content, 60)

    def test_fillParentTooFullWithNegativeTokens(self):
        """
        Test that adding negative tokens to a bucket with a parent also fills
        the parent bucket, but will not overfill it.
        """
        b2 = htb.Bucket(self.b1)
        b2.maxburst = 60
        b2.rate = 100
        b2.add(-10)
        self.assertEqual(b2.content, 0)
        self.assertEqual(self.b1.content, 0)

    def test_drip(self):
        """
        Test that a bucket loses tokens over time.
        """
        self.b1.add(60)
        sleep(1.2)
        self.b1.drip()
        self.assertEqual(self.b1.content, 0)

    def test_dripAllAtOnce(self):
        """
        Test that a bucket loses tokens over time, immediately if its rate is
        L{None}.
        """
        self.b1.add(60)
        self.b1.rate = None
        self.b1.drip()
        self.assertEqual(self.b1.content, 0)

    def test_dripNegativeTokens(self):
        """
        Test that a bucket never contains negative tokens.
        """
        self.b1.add(0)
        self.b1.drip()
        self.assertEqual(self.b1.content, 0)

    def test_dripAndAdd(self):
        """
        Test that a bucket can both drip and fill.
        """
        self.b1.add(60)
        sleep(1.2)
        self.b1.drip()
        self.b1.add(60)
        self.assertEqual(self.b1.content, 60)

    def test_dripAndAddToParent(self):
        """
        Test that a bucket can both drip and fill and the parent does the same.
        """
        b2 = htb.Bucket(self.b1)
        b2.maxburst = 200
        b2.rate = 100
        b2.add(60)
        sleep(1.2)
        b2.drip()
        b2.add(60)
        self.assertEqual(b2.content, 60)
        self.assertEqual(self.b1.content, 60)


class HierarchicalBucketFilterTests(TestCase):
    """
    Tests for L{htb.HierarchicalBucketFilter}.
    """

    def setUp(self):
        """
        Set up a L{HierarchicalBucketFilter}.
        """
        self.f = htb.HierarchicalBucketFilter()
        self.c = Clock()
        self.f.time = self.c.seconds

    def test_sweep(self):
        """
        Test that the L{HierarchicalBucketFilter} will sweep out empty
        buckets.
        """
        self.f.sweepInterval = 10
        bucket = self.f.getBucketFor()
        bucket.content = 1
        self.c.advance(10)
        self.f.getBucketFor()
        self.assertIn(None, self.f.buckets)
        bucket.content = 0
        self.c.advance(10)
        self.f.getBucketFor()
        self.assertNotIn(None, self.f.buckets)


class MockTransport:
    """
    Mock L{ITransport} to be used in tests.
    """

    def __init__(self, peer=None, host=None):
        self.peer = peer
        self.host = host

    def getPeer(self):
        """
        Return the peer information.
        """
        return self.peer

    def getHost(self):
        """
        Return the host information.
        """
        return self.host


class FilterByHostTests(TestCase):
    """
    Tests for L{htb.FilterByHost}.
    """

    def setUp(self):
        """
        Set up a L{FilterByHost}.
        """
        self.f = htb.FilterByHost()
        self.c = Clock()
        self.f.time = self.c.seconds

    def test_sweep(self):
        """
        Test that the L{FilterByHost} will sweep out empty buckets.
        """
        self.f.sweepInterval = 10
        t = MockTransport(peer=("127.0.0.1", 8080))
        bucket = self.f.getBucketFor(t)
        bucket.content = 1
        self.c.advance(10)
        self.f.getBucketFor(t)
        self.assertIn(8080, self.f.buckets)
        bucket.content = 0
        self.c.advance(10)
        self.f.getBucketFor(t)
        self.assertNotIn(8080, self.f.buckets)


class FilterByServerTests(TestCase):
    """
    Tests for L{htb.FilterByServer}.
    """

    def setUp(self):
        """
        Set up a L{FilterByServer}.
        """
        self.f = htb.FilterByServer()
        self.c = Clock()
        self.f.time = self.c.seconds

    def test_sweep(self):
        """
        Test that the L{FilterByServer} will sweep out empty buckets.
        """
        self.f.sweepInterval = 10
        t = MockTransport(host=("127.0.0.1", 8080, 1))
        bucket = self.f.getBucketFor(t)
        bucket.content = 1
        self.c.advance(10)
        self.f.getBucketFor(t)
        self.assertIn(1, self.f.buckets)
        bucket.content = 0
        self.c.advance(10)
        self.f.getBucketFor(t)
        self.assertNotIn(1, self.f.buckets)


@implementer(interfaces.ITransport)
class ShapedTransportTests(TestCase):
    """
    Tests for L{htb.ShapedTransport}.
    """

    def test_getattr(self):
        """
        Test that L{htb.ShapedTransport} will redirect attribute lookups to
        its consumer.
        """
        transport = MockTransport()
        consumer = htb.ShapedTransport(transport, htb.Bucket())
        self.assertEqual(consumer.getPeer(), transport.getPeer())


class ShapedProtocolFactoryTests(TestCase):
    """
    Tests for L{htb.ShapedProtocolFactory}.
    """

    def test_wraps_makeConnection(self):
        """
        Test that L{htb.ShapedProtocolFactory} will wrap the
        L{Protocol}'s makeConnection method to use a L{ShapedTransport}.
        """
        bucket = htb.Bucket()
        protocol = htb.ShapedProtocolFactory(TestCase, htb.HierarchicalBucketFilter())
        proto = protocol()
        proto.makeConnection(MockTransport(peer=("127.0.0.1", 8080)))
        self.assertIsInstance(proto.transport, htb.ShapedTransport)


class ShapedConsumerTests(TestCase):
    """
    Tests for L{htb.ShapedConsumer}.
    """

    def setUp(self):
        """
        Set up a L{ShapedConsumer}.
        """
        self.consumer = htb.ShapedConsumer(MockTransport(), htb.Bucket())

    def test_stopProducing(self):
        """
        Test that L{htb.ShapedConsumer.stopProducing} will decrement
        the bucket's _refcount.
        """
        self.consumer.stopProducing()
        self.assertEqual(self.consumer.bucket._refcount, 0)


class BucketTests(TestCase):
    """
    Tests for L{htb.Bucket}.
    """

    def setUp(self):
        """
        Set up a L{htb.Bucket}.
        """
        self.bucket = htb.Bucket()

    def test_add(self):
        """
        Test that L{htb.Bucket.add} will add tokens to the bucket.
        """
        self.bucket.add(10)
        self.assertEqual(self.bucket.content, 10)

    def test_drip(self):
        """
        Test that L{htb.Bucket.drip} will remove tokens from the bucket.
        """
        self.bucket.add(10)
        self.bucket.drip()
        self.assertEqual(self.bucket.content, 0)


class HierarchicalBucketFilterTests(TestCase):
    """
    Tests for L{htb.HierarchicalBucketFilter}.
    """

    def setUp(self):
        """
        Set up a L{htb.HierarchicalBucketFilter}.
        """
        self.filter = htb.HierarchicalBucketFilter()

    def test_getBucketFor(self):
        """
        Test that L{htb.HierarchicalBucketFilter.getBucketFor} will return a
        L{htb.Bucket}.
        """
        bucket = self.filter.getBucketFor()
        self.assertIsInstance(bucket, htb.Bucket)


class FilterByHostTests(TestCase):
    """
    Tests for L{htb.FilterByHost}.
    """

    def setUp(self):
        """
        Set up a L{htb.FilterByHost}.
        """
        self.filter = htb.FilterByHost()

    def test_getBucketKey(self):
        """
        Test that L{htb.FilterByHost.getBucketKey} will return the peer's
        port.
        """
        transport = MockTransport(peer=("127.0.0.1", 8080))
        key = self.filter.getBucketKey(transport)
        self.assertEqual(key, 8080)


class FilterByServerTests(TestCase):
    """
    Tests for L{htb.FilterByServer}.
    """

    def setUp(self):
        """
        Set up a L{htb.FilterByServer}.
        """
        self.filter = htb.FilterByServer()

    def test_getBucketKey(self):
        """
        Test that L{htb.FilterByServer.getBucketKey} will return the host's
        port.
        """
        transport = MockTransport(host=("127.0.0.1", 8080, 1))
        key = self.filter.getBucketKey(transport)
        self.assertEqual(key, 1)


class ShapedTransportTests(TestCase):
    """
    Tests for L{htb.ShapedTransport}.
    """

    def test_getattr(self):
        """
        Test that L{htb.ShapedTransport} will redirect attribute lookups to
        its consumer.
        """
        transport = MockTransport()
        consumer = htb.ShapedTransport(transport, htb.Bucket())
        self.assertEqual(consumer.getPeer(), transport.getPeer())


class ShapedProtocolFactoryTests(TestCase):
    """
    Tests for L{htb.ShapedProtocolFactory}.
    """

    def test_wraps_makeConnection(self):
        """
        Test that L{htb.ShapedProtocolFactory} will wrap the
        L{Protocol}'s makeConnection method to use a L{ShapedTransport}.
        """
        protocol = htb.ShapedProtocolFactory(TestCase, htb.HierarchicalBucketFilter())
        proto = protocol()
        proto.makeConnection(MockTransport(peer=("127.0.0.1", 8080)))
        self.assertIsInstance(proto.transport, htb.ShapedTransport)


class ShapedConsumerTests(TestCase):
    """
    Tests for L{htb.ShapedConsumer}.
    """

    def setUp(self):
        """
        Set up a L{ShapedConsumer}.
        """
        self.consumer = htb.ShapedConsumer(MockTransport(), htb.Bucket())

    def test_stopProducing(self):
        """
        Test that L{htb.ShapedConsumer.stopProducing} will decrement
        the bucket's _refcount.
        """
        self.consumer.stopProducing()
        self.assertEqual(self.consumer.bucket._refcount, 0)