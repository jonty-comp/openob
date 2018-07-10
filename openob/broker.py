from openob.logger import LoggerFactory
import redis

class MessageBroker(object):
    _isSetup = False

    def __init__(self, element):
        if MessageBroker._isSetup is False:
            raise Exception('Message Broker has not been configured')
        self.logger_factory = LoggerFactory()
        self.logger = self.logger_factory.getLogger('broker.%s' % element.replace(':','.'))
        self.logger.info('Setting up message broker for %s' % element)
        self.element = element
        
    @staticmethod
    def setup(redis_host):        
        if MessageBroker._isSetup is False:
            MessageBroker.redis_host = redis_host
            logger_factory = LoggerFactory()
            logger = logger_factory.getLogger('broker')
            logger.info('Connecting to configuration host %s' % MessageBroker.redis_host)

            MessageBroker.redis = None
            while True:
                try:
                    MessageBroker.redis = redis.StrictRedis(
                        host=MessageBroker.redis_host,
                        charset='utf-8',
                        decode_responses=True
                    )
                    logger.info('Connected to Redis server at %s' % MessageBroker.redis_host)
                    break
                except Exception as e:
                    logger.error(
                        'Unable to connect to configuration host! Retrying. (%s)'
                        % e
                    )
                    time.sleep(0.1)
            MessageBroker._isSetup = True

    def scoped_key(self, key):
        """Return an appropriate key name scoped to an element"""
        return ("openob:%s:%s" % (self.element, key))

    def blocking_get(self, key):
        """Get a value, blocking until it's not None if needed"""
        while True:
            value = self.get(key)
            if value is not None:
                self.logger.debug('Fetched (blocking) %s, got %s' % (key, value))
                return value
            time.sleep(0.1)

    def set(self, key, value):
        """Set a value in the config store"""
        scoped_key = self.scoped_key(key)
        self.redis.set(scoped_key, value)
        self.logger.debug('Set %s to %s' % (key, value))
        return value

    def get(self, key):
        """Get a value from the config store"""
        scoped_key = self.scoped_key(key)
        value = self.redis.get(scoped_key)
        
        self.logger.debug('Fetched %s, got %s' % (key, value))
        return value

    def unset(self, key):
        """Unset a value from the config store"""
        scoped_key = self.scoped_key(key)
        self.redis.delete(scoped_key)
        self.logger.debug('Unset %s' % scoped_key)

    def __getattr__(self, key):
        """Convenience method to access get"""
        return self.get(key)
