from unittest import TestCase
from nose.plugins.attrib import attr
from shiftmemory import Memory, exceptions, adapter

class UserTests(TestCase):
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





