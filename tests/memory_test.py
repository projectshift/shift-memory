from unittest import TestCase, mock
from nose.plugins.attrib import attr
from shiftmemory import Memory, exceptions, adapter

class MemoryTest(TestCase):
    """ This holds tests for the main memory api """

    def setUp(self):
        TestCase.setUp(self)

        self.config = dict()

        # adapter
        self.config['dummy-one'] = dict(
            adapter='dummy',
            ttl=1,
            config='some adapter config'
        )
        self.config['not-implemented'] = dict(
            adapter='bad',
            ttl=1,
            config='some adapter config'
        )



    # -------------------------------------------------------------------------

    def test_testing(self):
        """ Can do testing """
        self.assertTrue(True)

    def test_creation(self):
        """ Can create an instance of memory """
        memory = Memory()
        self.assertIsInstance(memory, Memory)


    def test_configure(self):
        """ Configuring memory """
        memory = Memory(self.config)
        self.assertEqual(self.config, memory.config)


    def test_return_created_if_exists(self):
        """ Return previously created cache if it exists """

        name = 'somecache'
        cache = 'some cache adapter object'
        memory = Memory()
        memory.caches[name] = cache
        self.assertEqual(cache, memory.get_cache(name))


    def test_raise_on_creating_nonexistent_adapter(self):
        """ Raise on creating adapter that was not configured """
        with self.assertRaises(exceptions.ConfigurationException):
            memory = Memory()
            memory.get_cache('not-configured')


    def test_raise_on_not_implemented_adapter(self):
        """ Raise on creating adapter that is not implemented """
        with self.assertRaises(exceptions.AdapterMissingException):
            memory = Memory(self.config)
            memory.get_cache('not-implemented')


    def test_create_cache(self):
        """ Can create cache on demand from config """
        name = 'dummy-one'
        memory = Memory(self.config)
        self.assertIsInstance(memory.get_cache(name), adapter.Dummy)


    def test_cache_namespace_is_set_to_cache_name(self):
        """ Setting cache namespace to cache name from config """
        memory = Memory(self.config)
        cache = memory.get_cache('dummy-one')
        self.assertEqual('dummy-one', cache.namespace)


    def test_raise_feature_missing_on_clearing_by_namespace(self):
        """ Raise if adapter is unable to drop all """
        with self.assertRaises(exceptions.AdapterFeatureMissingException):
            memory = Memory(self.config)
            memory.drop_cache('dummy-one')


    def test_drop_cache_by_name(self):
        """ Dropping cache by name """
        memory = Memory()
        cache = mock.Mock()
        cache.delete_all.return_value = 'deleted'
        memory.caches['test'] = cache

        self.assertEqual('deleted', memory.drop_cache('test'))


    def test_drop_all_caches(self):
        """ Dropping all configured caches """
        config = dict(test=dict(adapter='test'))
        memory = Memory(config)

        cache = mock.Mock()
        memory.caches['test'] = cache

        memory.drop_all_caches()
        self.assertTrue(cache.delete_all.called)


    def test_raise_feature_missing_on_optimizing(self):
        """ Raise if adapter is unable to optimize """
        with self.assertRaises(exceptions.AdapterFeatureMissingException):
            memory = Memory(self.config)
            memory.optimize_cache('dummy-one')


    def test_optimize_cache_by_name(self):
        """ Optimizing cache by name """
        memory = Memory()
        memory.caches['test'] = mock.Mock()

        memory.optimize_cache('test')
        self.assertTrue(memory.caches['test'].optimize.called)


    def test_optimize_all_caches(self):
        """ Optimizing all configured caches """
        config = dict(test=dict(adapter='test'))
        memory = Memory(config)
        memory.caches['test'] = mock.Mock()

        memory.optimize_all_caches()
        self.assertTrue(memory.caches['test'].optimize.called)








