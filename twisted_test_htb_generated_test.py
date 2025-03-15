# -*- test-case-name: twisted.test.test_htb -*-
# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

"""
Tests for L{twisted.protocols.htb}.
"""

import time
import unittest

from twisted.protocols import htb, pcp


class TestBucket(unittest.TestCase):
    def test_noParent(self):
        b = htb.Bucket()
        # Infinite add
        self.assertEqual(b.add(1000), 1000)
        # Zero rate, infinite capacity
        b.rate = 0
        self.assertEqual(b.add(1000), 1000)
        # Zero rate, finite capacity
        b.maxburst = 100
        self.assertEqual(b.add(1000), 100)
        # Nonzero rate, finite capacity
        b.rate = 10
        self.assertEqual(b.add(1000), 100)
        # Drip to 90
        self.assertEqual(b.content, 100)
        b.lastDrip -= 1
        b.drip()
        self.assertEqual(b.content, 90)
        # Drip to 50
        b.lastDrip -= 4
        b.drip()
        self.assertEqual(b.content, 50)
        # Drip to 0
        b.lastDrip -= 5
        b.drip()
        self.assertEqual(b.content, 0)
        # Drip negative
        b.lastDrip -= 5
        b.drip()
        self.assertEqual(b.content, 0)

    def test_parent(self):
        parent = htb.Bucket()
        b = htb.Bucket(parent)
        # Infinite add
        self.assertEqual(b.add(1000), 1000)
        self.assertEqual(parent.content, 1000)
        # Zero rate, infinite capacity
        b.rate = 0
        self.assertEqual(b.add(1000), 1000)
        # Zero rate, finite capacity
        b.maxburst = 100
        self.assertEqual(b.add(1000), 100)
        # Nonzero rate, finite capacity
        b.rate = 10
        self.assertEqual(b.add(1000), 100)
        # Drip to 90
        self.assertEqual(b.content, 100)
        b.lastDrip -= 1
        b.drip()
        self.assertEqual(b.content, 90)
        # Drip to 50
        b.lastDrip -= 4
        b.drip()
        self.assertEqual(b.content, 50)
        # Drip to 0
        b.lastDrip -= 5
        b.drip()
        self.assertEqual(b.content, 0)
        # Drip negative
        b.lastDrip -= 5
        b.drip()
        self.assertEqual(b.content, 0)

    def test_infinite(self):
        b = htb.Bucket()
        b.maxburst = None
        b.rate = 10
        b.add(1000)
        b.content = 1000
        b.lastDrip -= 1
        b.drip()
        self.assertEqual(b.content, 990)

    def test_infiniteParent(self):
        b = htb.Bucket()
        b.maxburst = None
        b.rate = 10
        c = htb.Bucket(b)
        c.add(1000)
        c.content = 1000
        c.lastDrip -= 1
        c.drip()
        self.assertEqual(c.content, 990)


class TestHierarchicalBucketFilter(unittest.TestCase):
    def setUp(self):
        self.hbf = htb.HierarchicalBucketFilter()

    def tearDown(self):
        self.hbf = None

    def test_getBucketFor(self):
        self.assertIsInstance(self.hbf.getBucketFor("foo"), htb.Bucket)
        self.assertIs(self.hbf.getBucketFor("foo"), self.hbf.getBucketFor("foo"))
        self.assertIsNot(self.hbf.getBucketFor("foo"), self.hbf.getBucketFor("bar"))

    def test_sweep(self):
        self.hbf.sweepInterval = 0
        b = self.hbf.getBucketFor("foo")
        b.maxburst = 100
        b.rate = 10
        b.lastDrip -= 1
        b.content = 10
        self.assertEqual(len(self.hbf.buckets), 1)
        self.hbf.sweep()
        self.assertEqual(len(self.hbf.buckets), 1)
        b.lastDrip -= 1
        self.hbf.sweep()
        self.assertEqual(len(self.hbf.buckets), 0)


class TestFilterByHost(unittest.TestCase):
    def setUp(self):
        self.fbh = htb.FilterByHost()

    def tearDown(self):
        self.fbh = None

    def test_getBucketKey(self):
        class DummyTransport:
            def getPeer(self):
                return (1, 2, 3)

        t = DummyTransport()
        self.assertEqual(self.fbh.getBucketKey(t), 2)


class TestFilterByServer(unittest.TestCase):
    def setUp(self):
        self.fbs = htb.FilterByServer()

    def tearDown(self):
        self.fbs = None

    def test_getBucketKey(self):
        class DummyTransport:
            def getHost(self):
                return (1, 2, 3)

        t = DummyTransport()
        self.assertEqual(self.fbs.getBucketKey(t), 3)


class TestShapedConsumer(unittest.TestCase):
    def setUp(self):
        self.bucket = htb.Bucket()
        self.consumer = pcp.BasicProducerConsumerProxy(None)
        self.sc = htb.ShapedConsumer(self.consumer, self.bucket)

    def tearDown(self):
        self.sc = None
        self.consumer = None
        self.bucket = None

    def test_initialization(self):
        self.assertEqual(self.bucket._refcount, 1)

    def test_stopProducing(self):
        self.sc.stopProducing()
        self.assertEqual(self.bucket._refcount, 0)


class TestShapedTransport(TestShapedConsumer):
    def setUp(self):
        self.bucket = htb.Bucket()
        self.consumer = pcp.BasicProducerConsumerProxy(None)
        self.st = htb.ShapedTransport(self.consumer, self.bucket)

    def tearDown(self):
        self.st = None
        self.consumer = None
        self.bucket = None

    def test_getattr(self):
        self.assertRaises(AttributeError, getattr, self.st, "foo")
        self.consumer.foo = 1
        self.assertEqual(self.st.foo, 1)
        self.assertEqual(getattr(self.st, "foo"), 1)


class TestShapedProtocolFactory(unittest.TestCase):
    def test_shapedProtocolFactory(self):
        bucketFilter = htb.FilterByHost()
        protocolFactory = htb.ShapedProtocolFactory(pcp.BasicProducerConsumerProxy, bucketFilter)
        protocol = protocolFactory()
        self.assertIsInstance(protocol, pcp.BasicProducerConsumerProxy)