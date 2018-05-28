from unittest import TestCase, mock
from nose.plugins.attrib import attr
from redis import StrictRedis
import time

from shiftmemory import Memory, exceptions
from shiftmemory.adapter import Redis


@attr('integration', 'redis')
class RedisTest(TestCase):
    """ This holds tests for the main memory api """

    def tearDown(self):
        redis = Redis('test')
        redis.get_redis().flushdb()
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
        adapter = Redis(
            namespace='test',
            unix_socket_path='/tmp/run/redis.sock',
            optimize_after=None
        )
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

    def test_check_item_existence(self):
        """ Can check item existence in cache """
        key = 'somekey'
        data = 'some date to put to cache'
        redis = Redis('test')
        redis.set(key,data)
        self.assertTrue(redis.exists(key))
        self.assertFalse(redis.exists('no-item'))

    def test_can_set(self):
        """ Simple item set """
        key = 'somekey'
        data = 'some date to put to cache'
        redis = Redis('test')
        redis.set(key,data)
        full_key = redis.get_full_item_key(key)
        self.assertIsNotNone(redis.get_redis().hget(full_key, 'data'))

    def test_can_set_with_ttl(self):
        """ Doing set item with custom ttl"""
        ttl = 1
        key = 'somekey'
        data = 'some date to put to cache'
        redis = Redis('test')
        redis.set(key,data, ttl=ttl)
        full_key = redis.get_full_item_key(key)
        time.sleep(1)
        self.assertIsNone(redis.get_redis().hget(full_key, 'data'))

    def test_can_set_with_expiration(self):
        """ Doing set item with expiration """
        key = 'somekey'
        data = 'some date to put to cache'
        expire = '+1second'
        redis = Redis('test')
        redis.set(key, data, expires_at=expire)
        full_key = redis.get_full_item_key(key)
        time.sleep(1.1)
        self.assertIsNone(redis.get_redis().hget(full_key, 'data'))

    def test_can_set_with_tags(self):
        """ Doing set item with tags """
        key = 'somekey'
        data = 'some date to put to cache'
        tags = ['tag']
        redis = Redis('test')
        redis.set(key,data, tags=tags)
        item_tags = redis.get_item_tags(key)
        tagged_items = redis.get_tagged_items('tag')
        self.assertIn('tag', item_tags)
        self.assertIn(redis.get_full_item_key(key), tagged_items)

    def test_can_add_item(self):
        """ Add item if not exist """
        key = 'itemkey'
        data1 = 'initial item data'
        data2 = 'updated item data'
        redis = Redis('test')
        self.assertTrue(redis.add(key, data1))
        self.assertFalse(redis.add(key, data2))
        self.assertEqual(data1, redis.get(key))

    def test_can_get_by_key(self):
        """ Getting item by key """
        key = 'itemkey'
        data = 'initial item data'
        redis = Redis('test')
        self.assertTrue(redis.set(key, data))
        self.assertEqual(data, redis.get(key))

    def test_can_delete_by_key(self):
        """ Deleting item by key """
        key = 'itemkey'
        data = 'initial item data'
        redis = Redis('test')
        redis.set(key, data)
        self.assertIsNotNone(redis.get(key))
        result = redis.delete(key)
        self.assertTrue(result)
        self.assertIsNone(redis.get(key))

    def test_can_delete_by_tags(self):
        """ Deleting items by tags """
        key1 = 'itemkey'
        data1 = 'initial item data'

        key2 = 'itemkey2'
        data2 = 'more initial item data'

        key3 = 'itemkey3'
        data3 = 'and some more initial item data'

        tags1 = ['tag1', 'tag2']
        tags2 = ['tag3', 'tag4']

        redis = Redis('test')
        redis.set(key1, data1, tags=tags1)
        redis.set(key2, data2, tags=tags1)
        redis.set(key3, data3, tags=tags2)

        redis.delete(tags=tags1)
        self.assertIsNone(redis.get(key1))
        self.assertIsNone(redis.get(key2))
        self.assertIsNotNone(redis.get(key3))

    def test_can_delete_by_tags_with_disjunction(self):
        """ Deleting by tags with disjunction """
        key1 = 'itemkey'
        data1 = 'initial item data'

        key2 = 'itemkey2'
        data2 = 'more initial item data'

        key3 = 'itemkey3'
        data3 = 'and some more initial item data'

        tags1 = ['tag1', 'tag2', 'tag3']
        tags2 = ['tag3', 'tag4']

        redis = Redis('test')
        redis.set(key1, data1, tags=tags1)
        redis.set(key2, data2, tags=tags1)
        redis.set(key3, data3, tags=tags2)

        redis.delete(tags=tags1, disjunction=True)
        self.assertIsNone(redis.get(key1))
        self.assertIsNone(redis.get(key2))
        self.assertIsNone(redis.get(key3))

    def test_can_delete_all(self):
        """ Deleting all items under namespace """
        key1 = 'itemkey'
        data1 = 'initial item data'

        key2 = 'itemkey2'
        data2 = 'some more initial item data'

        redis = Redis('test')
        redis.set(key1, data1)
        redis.set(key2, data2)

        self.assertIsNotNone(redis.get(key1))
        self.assertIsNotNone(redis.get(key2))

        redis.delete_all()

        self.assertIsNone(redis.get(key1))
        self.assertIsNone(redis.get(key2))

    def test_set_item_tags(self):
        """ Setting item tags """

        key1 = 'somekey'
        data1 = 'some date to put to cache'
        key2 = 'other'
        data2 = 'some other data'


        redis = Redis('test')
        redis.set(key1, data1)
        redis.set(key2, data2)

        tags = ['tag1', 'tag2']
        redis.set_tags(key1, tags)
        redis.set_tags(key2, tags)

        set1 = redis.get_tagged_items('tag1')
        set2 = redis.get_tagged_items('tag2')

        # assert tags created and contain item
        self.assertTrue(type(set1) is set)
        self.assertTrue(redis.get_full_item_key(key1) in set1)
        self.assertTrue(redis.get_full_item_key(key2) in set1)

        self.assertTrue(type(set2) is set)
        self.assertTrue(redis.get_full_item_key(key1) in set2)
        self.assertTrue(redis.get_full_item_key(key2) in set2)

    def test_get_item_tags(self):
        """ Getting item tags """
        key = 'somekey'
        data = 'some date to put to cache'

        redis = Redis('test')
        redis.set(key, data)

        tags = ['tag1', 'tag2']
        redis.set_tags(key, tags)

        # assert item tagged
        item_tags = redis.get_item_tags(key)
        self.assertTrue(type(item_tags) is list)
        self.assertIn('tag1', item_tags)
        self.assertIn('tag2', item_tags)

        self.assertIsNone(redis.get_item_tags('no-item'))

    # -------------------------------------------------------------------------
    # Optimizing
    # -------------------------------------------------------------------------

    def test_can_optimize(self):
        """ Performing storage optimization """

        redis = Redis('test')
        data = 'this data will be used for everything'

        key1 = 'item1'; tags1=['tag1', 'tag2', 'tag3']
        key2 = 'item2'; tags2=['tag1', 'tag2', 'tag3']
        key3 = 'item3'; tags3=['tag3', 'tag4', 'tag5']
        key4 = 'item4'; tags4=['tag3', 'tag4', 'tag5']

        redis.set(key1, data, ttl=1, tags=tags1)
        redis.set(key2, data, ttl=1, tags=tags2)

        redis.set(key3, data, tags=tags3)
        redis.set(key4, data, tags=tags4)

        redis.get_redis().delete(redis.get_tag_set_key('tag4'))
        redis.get_redis().delete(redis.get_tag_set_key('tag5'))

        time.sleep(1.1)
        redis.optimize()

        # missing items should be removed from tags
        self.assertNotIn(
            redis.get_full_item_key(key1),
            redis.get_tagged_items('tag3')
        )
        self.assertNotIn(
            redis.get_full_item_key(key2),
            redis.get_tagged_items('tag3')
        )

        # empty tags should be removed
        self.assertFalse(redis.get_tagged_items('tag1'))
        self.assertFalse(redis.get_tagged_items('tag2'))

        # missing tags should be removed from items
        self.assertNotIn('tag4', redis.get_item_tags('item3'))
        self.assertNotIn('tag4', redis.get_item_tags('item4'))
        self.assertNotIn('tag5', redis.get_item_tags('item3'))
        self.assertNotIn('tag5', redis.get_item_tags('item4'))

    def test_collect_garbage_initial(self):
        """ Garbage collect does nothing on first run """
        redis = Redis('test')
        gc_key = redis.get_full_item_key('__gc')
        self.assertIsNotNone(redis.get(gc_key))

    def test_collect_garbage_returns_false_if_not_the_time(self):
        """ Garbage collect returns false if  its not the time"""
        redis = Redis('test')
        self.assertFalse(redis.collect_garbage())

    def test_collect_garbage(self):
        """ Can do garbage collection after timeout """
        redis = Redis('test', optimize_after='+1 second')
        time.sleep(1.1)
        self.assertTrue(redis.collect_garbage())





