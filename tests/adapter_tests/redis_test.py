from unittest import TestCase, mock
from nose.plugins.attrib import attr
from redis import StrictRedis

from shiftmemory import Memory, exceptions
from shiftmemory.adapter import Redis

@attr('integration')
class RedisTest(TestCase):
    """ This holds tests for the main memory api """

    def tearDown(self):
        # redis = Redis('test')
        # redis.get_redis().flushdb()
        TestCase.tearDown(self)


    # -------------------------------------------------------------------------

    def test_create_adapter(self):
        """ Creating adapter """
        adapter = Redis('test')
        self.assertIsInstance(adapter, Redis)


    def test_default_config(self):
        """ Use default configuration options if non provided """
        adapter = Redis('test')
        self.assertEqual(60, adapter.ttl)
        self.assertEqual('localhost', adapter.config['host'])
        self.assertEqual(6379, adapter.config['port'])
        self.assertEqual(0, adapter.config['db'])


    def test_merge_config_with_defaults(self):
        """ Merge config options with defaults to get missing """
        adapter = Redis(namespace='test', host='127.0.0.1', db=2)
        self.assertEqual('127.0.0.1', adapter.config['host'])
        self.assertEqual(6379, adapter.config['port'])
        self.assertEqual(2, adapter.config['db'])


    def test_use_unix_socket_if_provided(self):
        """ Drop tcp socket and use unix socket if configured """
        adapter = Redis(namespace='test',unix_socket_path='/tmp/run/redis.sock')
        self.assertFalse('host' in adapter.config)
        self.assertFalse('port' in adapter.config)
        self.assertTrue('unix_socket_path' in adapter.config)


    def test_get_redis(self):
        """ Getting redis connection """
        adapter = Redis('testing')
        redis = adapter.get_redis()
        self.assertIsInstance(redis, StrictRedis)


    def test_can_put_to_redis(self):
        """ Can do basic put to storage """
        redis = Redis('testing')
        redis.get_redis().set('foo', 'bar')
        result = redis.get_redis().get('foo')
        if result:
            result = result.decode()

        self.assertEqual('bar', result)


    # -------------------------------------------------------------------------
    # Keys
    # -------------------------------------------------------------------------

    def test_get_full_key(self):
        """ Generating full namespaced key from short cache key"""

        namespace = 'testing'
        separator = '::'
        key = 'some-key'

        redis = Redis(namespace)
        full_key = redis.get_full_item_key(key)
        self.assertEqual(namespace + separator + key, full_key)


    def test_return_key_if_already_full(self):
        """ Do not create full key from full key, just return """

        namespace = 'testing'
        separator = '::'
        key = 'some-key'

        redis = Redis(namespace)
        full_key = redis.get_full_item_key(key)
        self.assertEqual(full_key, redis.get_full_item_key(full_key))


    def test_can_detect_full_keys(self):
        """ Detecting full item key """

        namespace = 'testing'
        key = 'some-key'
        redis = Redis(namespace)

        full_key = redis.get_full_item_key(key)
        not_full_key = 'x' + full_key
        bogus = 'bad'

        self.assertTrue(redis.is_full_item_key(full_key))
        self.assertFalse(redis.is_full_item_key(not_full_key))
        self.assertFalse(redis.is_full_item_key(bogus))


    def test_get_tag_key(self):
        """ Get full key for a tag set from tag name"""
        namespace = 'testing'
        tag = 'tagged'
        sep = '::'

        redis = Redis(namespace)
        tag_key = redis.get_tag_set_key(tag)
        expected = namespace + sep + 'tags' + sep + tag
        self.assertEqual(expected, tag_key)


    # -------------------------------------------------------------------------
    # Cache
    # -------------------------------------------------------------------------


    def test_check_ttl_support(self):
        """ Can check for redis TTL support"""
        redis = Redis('test')
        self.assertTrue(redis.check_ttl_support())

        redis.redis = mock.Mock()
        redis.redis.info.return_value = dict(redis_version='1.1.1')
        with self.assertRaises(exceptions.AdapterFeatureMissingException):
            redis.check_ttl_support()


    def test_can_set(self):
        """ Simple item set """
        key = 'somekey'
        data = 'some date to put to cache'
        ttl = 60

        redis = Redis('test')
        redis.set(key,data,ttl=ttl)

        full_key = redis.get_full_item_key(key)
        self.assertIsNotNone(redis.get_redis().hget(full_key, 'data'))



    def test_check_item_existence(self):
        """ Can check item existence in cache """
        key = 'somekey'
        data = 'some date to put to cache'

        redis = Redis('test')
        redis.set(key,data)

        self.assertTrue(redis.exists(key))
        self.assertFalse(redis.exists('no-item'))
