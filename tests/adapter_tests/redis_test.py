from unittest import TestCase, mock
from nose.plugins.attrib import attr
from redis import StrictRedis

from shiftmemory import Memory, exceptions
from shiftmemory.adapter import Redis

@attr('integration')
class RedisTest(TestCase):
    """ This holds tests for the main memory api """

    def setUp(self):
        TestCase.setUp(self)

        self.config = dict()

        # adapter
        self.config['testing'] = dict(
            adapter='redis',
            ttl=1,
            config=dict()
        )



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
        config = dict(host='127.0.0.1', db=2)
        adapter = Redis(namespace='test', config=config)
        self.assertEqual('127.0.0.1', adapter.config['host'])
        self.assertEqual(6379, adapter.config['port'])
        self.assertEqual(2, adapter.config['db'])


    def test_use_unix_socket_if_provided(self):
        """ Drop tcp socket and use unix socket if configured """
        config = dict(unix_socket_path='/tmp/run/redis.sock')
        adapter = Redis(namespace='test', config=config)
        self.assertFalse('host' in adapter.config)
        self.assertFalse('port' in adapter.config)
        self.assertTrue('unix_socket_path' in adapter.config)


    def test_get_redis(self):
        """ Getting redis connection """
        adapter = Redis('testing')
        redis = adapter.get_redis()
        self.assertIsInstance(redis, StrictRedis)





