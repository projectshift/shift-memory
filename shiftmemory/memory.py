from shiftmemory import exceptions, adapter


class Memory():
    """
    Main memory API
    Keeps track of caches, configures and instantiates them on demand and
    provides means to perform operations on caches
    """

    def __init__(self, config=None):
        """
        Creates your memory instance.
        Just give it your caches configuration as a dictionary
        """
        self.caches = dict()
        self.config = dict()
        if config:
            self.config = config


    def get_cache(self, name):
        """
        Get cache
        Checks if a cache was already created and returns that. Otherwise
        attempts to create a cache from configuration and preserve
        for future use
        """
        if name in self.caches:
            return self.caches[name]

        if not name in self.config:
            error = 'Adapter [{}] is not configured'.format(name)
            raise exceptions.ConfigurationException(error)

        cache_config = self.config[name]
        adapter_name = cache_config['adapter']

        class_name = adapter_name[0].upper() + adapter_name[1:]
        if not hasattr(adapter, class_name):
            error = 'Adapter class [{}] is missing'.format(class_name)
            raise exceptions.AdapterMissingException(error)

        cls = getattr(adapter, class_name)
        cache = cls(
            namespace = name,
            config=cache_config['config'],
            ttl=cache_config['ttl'],
            )
        self.caches[name] = cache
        return self.caches[name]


    def drop_cache(self, name):
        """
        Drop cache
        Deletes all items in cache by name
        """
        cache = self.get_cache(name)
        if not hasattr(cache, 'delete_all'):
            cls = type(cache)
            error = 'Adapter [{}] can not drop cache by namespace'.format(cls)
            raise exceptions.AdapterFeatureMissingException(error)

        return cache.delete_all()


    def drop_all_caches(self):
        """
        Drop all caches
        Goes through every configured cache and drops all items. Will
        skip certain caches if they do not support drop all feature
        """
        for name in self.config.keys():
            cache = self.get_cache(name)
            if hasattr(cache, 'delete_all'):
                cache.delete_all(name)
        return True


    def optimize_cache(self, name):
        """
        Optimize cache
        gets cache by name and performs optimization if supported
        """
        cache = self.get_cache(name)
        if not hasattr(cache, 'optimize'):
            cls = type(cache)
            error = 'Adapter [{}] can not optimize itself'.format(cls)
            raise exceptions.AdapterFeatureMissingException(error)

        return cache.optimize()


    def optimize_all_caches(self):
        """
        Optimize all caches
        Goes through every configured cache and optimizes. Will
        skip certain caches if they do not support optimization feature
        """
        for name in self.config.keys():
            cache = self.get_cache(name)
            if hasattr(cache, 'optimize'):
                cache.optimize(name)
        return True






