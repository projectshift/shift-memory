from redis import StrictRedis
from shiftmemory import exceptions

class Redis:
    """
    Redis adapter
    Implements cache for items under namespaces in a single database. In
    addition each item can be marked by tags and can have optional custom
    expiration. You can then perform fetch or remove items by tags or
    namespaces.

    The way it works is that each cached item is stored as redis hash
    consisting of data and tags. Each tag is stored as redis set consisting
    of hash ids for tagged items.

    It is important to notice that expired items won't be removed from
    tags automatically, that is why you can optimize your cache with optimize
    command and there is a simple garbage collection in place.
    """

    def __init__(
        self,
        namespace,
        ttl=60,
        namespace_separator=None,
        **config
    ):
        """
        Create adapter
        Instantiates adapter with namespace, default ttl and optional
        connection configuration parameters

        :param namespace:       namespace name
        :param ttl:             default ttl for all items (default=60)
        :param config:          connection configuration (optional)
        :return:                None
        """
        self.redis = None
        self.ttl = ttl
        self.namespace = namespace

        self.namespace_separator = '::'
        if namespace_separator:
            self.namespace_separator = namespace_separator

        # key prefixes for items and tags
        self.item_prefix = self.namespace + self.namespace_separator
        self.tag_prefix = self.item_prefix + 'tags' + self.namespace_separator

        # init redis connection
        self.configure(config)


    def configure(self, config=None):
        """
        Configure
        Configures an adapter with optional config. If no config provided
        or it misses some settings, defaults will be used.

        :param config:          config dictionary
        :return:                None
        """
        default_config = dict(
            host='localhost',
            port=6379,
            db=0
        )

        if config is None: config = dict()
        self.config = dict(list(default_config.items()) + list(config.items()))

        if 'unix_socket_path' in self.config:
            del self.config['host'], self.config['port']


    def get_redis(self):
        """
        Get redis
        Checks if we have a connection and returns that. Otherwise creates
        one from config and preserves for future use

        :return:                redis.client.StrictRedis
        """
        if not self.redis:
            self.redis = StrictRedis(**self.config)

        return self.redis


    # -------------------------------------------------------------------------
    # Keys
    # -------------------------------------------------------------------------

    def get_full_item_key(self, key):
        """
        Get full item keys
        Returns normalized item cache key with a namespace prepended.
        This will be used to store a hash of data and tags

        :param key:             string key
        :return:                string normalized key
        """
        if self.is_full_item_key(key):
            return key

        key = self.item_prefix + key
        return key



    def is_full_item_key(self, key):
        """
        Is full item key?
        Checks if provided key is a full item cache key used for storage. It
        should contain prepended namespace.

        :param key:             string, key to check
        :return:                bool
        """
        return key.startswith(self.item_prefix)



    def get_tag_set_key(self, tag):
        """
        Get tag set key
        Returns tag set key used to store tagged items hash ids

        :param key:             string, tag
        :return:                string, tag set key
        """
        return self.tag_prefix + tag


    # -------------------------------------------------------------------------
    # Caching
    # -------------------------------------------------------------------------


    def check_ttl_support(self):
        """
        Check ttl support
        Checks major redis version to be >2 for ttl support and raises
        feature exception if it's not

        :return:                None
        """
        redis = self.get_redis()
        version = redis.info('server')['redis_version']
        major = int(version.split('.')[0])
        if major < 2:
            error = 'To use TTL you need Redis >= 2.0.0'
            raise exceptions.AdapterFeatureMissingException(error)

        return True


    def ttl_from_expiration(self, expires_at):
        """
        TTL from expiration
        Returns ttl in seconds until expiration date based on now

        :param expires_at:          date
        :return:                    int
        """
        return 10



    def set(self, key, value, tags=None, ttl=None, expires_at=None):
        """
        Set item
        Creates or updates and item (hash). Can optionally accept an iterable
        of tags to add to item and either ttl or expiration date for custom
        item expiration, otherwise falls back to default adapter ttl.

        :param key:             string, cache key
        :param value:           string, data to put
        :param tags:            iterable or None, any tags to add
        :param ttl:             int, optional custom ttl in seconds
        :param expires_at:      date, optional expiration date
        :return:                bool
        """

        redis = self.get_redis()
        multi = redis.pipeline()

        # data
        key = self.get_full_item_key(key)
        multi.hset(key, 'data', value)

        # expire
        if expires_at: ttl = self.ttl_from_expiration(expires_at)
        if not ttl: ttl = self.ttl
        multi.expire(key, ttl)

        # tag
        if tags: tags = list(tags)


        # commit
        multi.execute()
        return



    def add(self, key, value, tags=None, ttl=None, expires_at=None):
        pass



    def exists(self, key):
        pass

    def get(self, key=None, tags=None):
        pass

    def increment(self, key):
        pass

    def decrement(self, key):
        pass

    def delete(self, key=None, tags=None):
        pass

    def delete_all(self):
        pass




    # -------------------------------------------------------------------------
    # Optimizing
    # -------------------------------------------------------------------------