from redis import StrictRedis

class Redis:
    """
    Redis adapter
    Implements caching to redis backend
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
        if not self.redis: self.redis = StrictRedis(**self.config)
        return self.redis

