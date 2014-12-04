class Dummy:
    """
    This is a dummy adapter.
    It exists mostly for testing interfaces and does nothing, but returns
    success for every operation
    """
    def __init__(self, config, ttl):
        self.config = config
        self.ttl = ttl




