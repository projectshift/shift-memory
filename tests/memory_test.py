from unittest import TestCase, mock
from nose.plugins.attrib import attr
from shiftmemory import Memory, exceptions, adapter


class MemoryTest(TestCase):
    """ This holds tests for the main memory api """

    def setUp(self):
        TestCase.setUp(self)

        # adapters
        self.adapters = dict(
            dummy=dict(
                type='dummy',
                config={}
            ),
            bad=dict(
                type='bad',
                config={}
            )
        )

        # caches
        self.caches = dict(
            dummy_one=dict(
                adapter='dummy',
                ttl=10
            )
        )

    # -------------------------------------------------------------------------

    def test_creation(self):
        """ Can create an instance of memory """
        memory = Memory()
        self.assertIsInstance(memory, Memory)

    def test_configure(self):
        """ Configuring memory """
        memory = Memory(adapters=self.adapters, caches=self.caches)
        self.assertEqual(self.adapters, memory.adapters)
        self.assertEqual(self.caches, memory.caches)

    def test_return_created_cache_if_exists(self):
        """ Return previously created cache if it exists """
        name = 'somecache'
        cache = 'some cache adapter object'
        memory = Memory()
        memory._cache_instances[name] = cache
        self.assertEqual(cache, memory.get_cache(name))

    def test_raise_when_getting_not_configured_cache(self):
        """ Raise when getting cache that wasn't configured """
        with self.assertRaises(exceptions.ConfigurationException):
            memory = Memory(adapters=self.adapters, caches=self.caches)
            memory.get_cache('not-configured')

    def test_raise_on_creating_cache_with_nonexistent_adapter(self):
        """ Raise on creating adapter that was not configured """
        with self.assertRaises(exceptions.ConfigurationException):
            config = dict(adapters=dict(), caches=dict(
                badadapter=dict(adapter='not-configured')
            ))
            memory = Memory(config)
            memory.get_cache('badadapter')

    def test_raise_on_not_implemented_adapter(self):
        """ Raise on creating adapter that is not implemented """
        with self.assertRaises(exceptions.AdapterMissingException):
            memory = Memory(
                adapters=dict(bad=dict(type='noclass')),
                caches=dict(badadapter=dict(adapter='bad'))
            )
            memory.get_cache('badadapter')

    def test_create_cache(self):
        """ Can create cache on demand from config """
        name = 'dummy_one'
        memory = Memory(adapters=self.adapters, caches=self.caches)
        self.assertIsInstance(memory.get_cache(name), adapter.Dummy)

    def test_cache_namespace_is_set_to_cache_name(self):
        """ Setting cache namespace to cache name from config """
        memory = Memory(adapters=self.adapters, caches=self.caches)
        cache = memory.get_cache('dummy_one')
        self.assertEqual('dummy_one', cache.namespace)

    def test_raise_feature_missing_on_clearing_by_namespace(self):
        """ Raise if adapter is unable to drop all """
        with self.assertRaises(exceptions.AdapterFeatureMissingException):
            memory = Memory(adapters=self.adapters, caches=self.caches)
            memory.drop_cache('dummy_one')

    def test_drop_cache_by_name(self):
        """ Dropping cache by name """
        memory = Memory()
        cache = mock.Mock()
        cache.delete_all.return_value = 'deleted'
        memory._cache_instances['test'] = cache
        self.assertEqual('deleted', memory.drop_cache('test'))

    def test_drop_all_caches(self):
        """ Dropping all configured caches """
        memory = Memory(
            adapters=self.adapters,
            caches=dict(test=dict(adapter='test'))
        )
        cache = mock.Mock()
        memory._cache_instances['test'] = cache
        memory.drop_all_caches()
        self.assertTrue(cache.delete_all.called)

    def test_raise_feature_missing_on_optimizing(self):
        """ Raise if adapter is unable to optimize """
        with self.assertRaises(exceptions.AdapterFeatureMissingException):
            memory = Memory(adapters=self.adapters, caches=self.caches)
            memory.optimize_cache('dummy_one')

    def test_optimize_cache_by_name(self):
        """ Optimizing cache by name """
        memory = Memory()
        memory._cache_instances['test'] = mock.Mock()

        memory.optimize_cache('test')
        self.assertTrue(memory._cache_instances['test'].optimize.called)

    def test_optimize_all_caches(self):
        """ Optimizing all configured caches """
        memory = Memory(
            adapters=self.adapters,
            caches=dict(test=dict(adapter='test'))
        )
        memory._cache_instances['test'] = mock.Mock()
        memory.optimize_all_caches()
        self.assertTrue(memory._cache_instances['test'].optimize.called)

    # -------------------------------------------------------------------------

    # INTEGRATION TESTS

    @attr('integration', 'redis')
    def test_create_cache_with_redis_adapter(self):
        """ Creating cache with redis adapter """
        adapters = dict(
            redis_adapter=dict(
                type='redis',
                config=dict(
                    host='localhost',
                    db=1
                )
            )
        )

        caches = dict(
            demo_redis=dict(
                adapter='redis_adapter',
                ttl=20
            )
        )

        memory = Memory(adapters=adapters, caches=caches)
        cache = memory.get_cache('demo_redis')
        self.assertIsInstance(cache, adapter.Redis)








