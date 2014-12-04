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
        config=None,
        namespace_separator=None
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

        # redis key prefixes for items and tags
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
        redis = self.get_redis()
        version = redis.info('server')['redis_version']
        major = int(version.split('.')[0])
        if major < 2:
            error = 'To use TTL you need Redis >= 2.0.0'
            raise exceptions.AdapterFeatureMissingException(error)

        return True




    # -------------------------------------------------------------------------
    # Optimizing
    # -------------------------------------------------------------------------