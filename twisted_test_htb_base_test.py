# -*- test-case-name: twisted.test.test_htb -*-
# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

from twisted.trial import unittest
from twisted.test.test_htb import (
    Bucket,
    HierarchicalBucketFilter,
    FilterByHost,
    FilterByServer,
    ShapedConsumer,
    ShapedTransport,
    ShapedProtocolFactory,
)
from twisted.protocols import pcp
from zope.interface import implementer
from twisted.internet import interfaces
from time import time


class BucketTests(unittest.TestCase):
    def setUp(self):
        self.bucket = Bucket()

    def test_initialization(self):
        self.assertEqual(self.bucket.content, 0)
        self.assertIsNone(self.bucket.parentBucket)
        self.assertGreater(self.bucket.lastDrip, 0)

    def test_add_without_limit(self):
        self.bucket.maxburst = None
        added_tokens = self.bucket.add(100)
        self.assertEqual(added_tokens, 100)
        self.assertEqual(self.bucket.content, 100)

    def test_add_with_limit(self):
        self.bucket.maxburst = 50
        added_tokens = self.bucket.add(100)
        self.assertEqual(added_tokens, 50)
        self.assertEqual(self.bucket.content, 50)

    def test_drip_no_rate(self):
        self.bucket.rate = None
        self.bucket.add(100)
        self.bucket.drip()
        self.assertEqual(self.bucket.content, 0)

    def test_drip_with_rate(self):
        self.bucket.rate = 10
        self.bucket.add(100)
        self.bucket.lastDrip -= 10  # Simulate 10 seconds passed
        self.bucket.drip()
        self.assertEqual(self.bucket.content, 0)  # Dripped completely


class HierarchicalBucketFilterTests(unittest.TestCase):
    def setUp(self):
        self.filter = HierarchicalBucketFilter()

    def test_get_bucket_for(self):
        bucket = self.filter.getBucketFor()
        self.assertIsInstance(bucket, Bucket)

    def test_sweep(self):
        bucket = self.filter.getBucketFor()
        bucket.add(10)
        self.filter.sweep()
        self.assertIn(self.filter.getBucketKey(), self.filter.buckets)

        bucket.content = 0
        self.filter.sweep()
        self.assertNotIn(self.filter.getBucketKey(), self.filter.buckets)


class FilterByHostTests(unittest.TestCase):
    def setUp(self):
        self.filter = FilterByHost()

    def test_get_bucket_key(self):
        transport = unittest.mock.Mock()
        transport.getPeer.return_value = ("127.0.0.1", 8080)
        key = self.filter.getBucketKey(transport)
        self.assertEqual(key, 8080)


class FilterByServerTests(unittest.TestCase):
    def setUp(self):
        self.filter = FilterByServer()

    def test_get_bucket_key(self):
        transport = unittest.mock.Mock()
        transport.getHost.return_value = ("127.0.0.1", 8080, "service")
        key = self.filter.getBucketKey(transport)
        self.assertEqual(key, "service")


class ShapedConsumerTests(unittest.TestCase):
    def setUp(self):
        self.consumer = unittest.mock.Mock()
        self.bucket = Bucket()
        self.sc = ShapedConsumer(self.consumer, self.bucket)

    def test_write_some_data(self):
        self.bucket.maxburst = None
        self.sc._writeSomeData(b"data")
        self.consumer.write.assert_called_once_with(b"data")

    def test_stop_producing(self):
        self.sc.stopProducing()
        self.consumer.stopProducing.assert_called_once()
        self.assertEqual(self.bucket._refcount, 0)


class ShapedTransportTests(unittest.TestCase):
    def setUp(self):
        self.transport = unittest.mock.Mock(spec=interfaces.ITransport)
        self.bucket = Bucket()
        self.st = ShapedTransport(self.transport, self.bucket)

    def test_getattr(self):
        self.transport.getPeer.return_value = "peer"
        self.assertEqual(self.st.getPeer(), "peer")


class ShapedProtocolFactoryTests(unittest.TestCase):
    def setUp(self):
        self.protocol = unittest.mock.Mock(spec=interfaces.IProtocol)
        self.bucketFilter = HierarchicalBucketFilter()
        self.factory = ShapedProtocolFactory(self.protocol, self.bucketFilter)

    def test_make_connection(self):
        proto_instance = self.factory()
        transport = unittest.mock.Mock()
        proto_instance.makeConnection(transport)
        self.assertIsInstance(
            proto_instance.makeConnection.__self__, ShapedTransport
        )