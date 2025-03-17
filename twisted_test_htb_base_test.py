import pytest
from twisted.test_htb.test_htb import Bucket, HierarchicalBucketFilter, FilterByHost, FilterByServer, ShapedConsumer, ShapedTransport, ShapedProtocolFactory
from twisted.protocols import pcp

class MockTransport:
    def getPeer(self):
        return ('mockpeer', 12345)

    def getHost(self):
        return ('mockhost', 80)

@pytest.fixture
def bucket():
    return Bucket()

@pytest.fixture
def parent_bucket():
    return Bucket()

@pytest.fixture
def hierarchical_bucket_filter():
    return HierarchicalBucketFilter()

@pytest.fixture
def filter_by_host():
    return FilterByHost()

@pytest.fixture
def filter_by_server():
    return FilterByServer()

@pytest.fixture
def shaped_consumer():
    consumer = pcp.BasicProducerConsumerProxy(None)
    bucket = Bucket()
    return ShapedConsumer(consumer, bucket)

@pytest.fixture
def shaped_transport():
    consumer = pcp.BasicProducerConsumerProxy(MockTransport())
    bucket = Bucket()
    return ShapedTransport(consumer, bucket)

def test_bucket_add(bucket):
    bucket.maxburst = 10
    added_tokens = bucket.add(5)
    assert added_tokens == 5
    assert bucket.content == 5

def test_bucket_add_with_parent(bucket, parent_bucket):
    parent_bucket.maxburst = 10
    bucket.parentBucket = parent_bucket
    added_tokens = bucket.add(5)
    assert added_tokens == 5
    assert bucket.content == 5
    assert parent_bucket.content == 5

def test_bucket_drip(bucket):
    bucket.rate = 1
    bucket.add(5)
    bucket.drip()
    assert bucket.content < 5

def test_hierarchical_bucket_filter_get_bucket_for(hierarchical_bucket_filter):
    transport = MockTransport()
    bucket = hierarchical_bucket_filter.getBucketFor(transport)
    assert isinstance(bucket, Bucket)

def test_filter_by_host_get_bucket_key(filter_by_host):
    transport = MockTransport()
    key = filter_by_host.getBucketKey(transport)
    assert key == 12345

def test_filter_by_server_get_bucket_key(filter_by_server):
    transport = MockTransport()
    key = filter_by_server.getBucketKey(transport)
    assert key == 80

def test_shaped_consumer_write(shaped_consumer):
    shaped_consumer.write(b"data")
    assert shaped_consumer._buffer == []

def test_shaped_transport_getattr(shaped_transport):
    peer = shaped_transport.getPeer()
    assert peer == ('mockpeer', 12345)

def test_shaped_protocol_factory():
    proto_class = lambda: pcp.BasicProducerConsumerProxy(None)
    bucket_filter = HierarchicalBucketFilter()
    factory = ShapedProtocolFactory(proto_class, bucket_filter)
    proto = factory()
    assert callable(proto.makeConnection)