import redis
import time
from openob.logger import LoggerFactory
from openob.broker import MessageBroker

class LinkConfig(object):

    """
        The LinkConfig class encapsulates link configuration. It's genderless;
        a TX node should be able to set up a new link and an RX node should be
        able (once the TX node has specified the port caps) to configure itself
        to receive the stream using the data and methods in this config.
    """

    int_properties = ['port', 'jitter_buffer', 'opus_framesize', 'opus_complexity', 'bitrate', 'opus_loss_expectation']
    bool_properties = ['opus_dtx', 'opus_fec', 'multicast']

    def __init__(self, link_name):
        """
            Set up a new LinkConfig instance - needs to know the link name
        """
        self.link_name = link_name
        self.logger_factory = LoggerFactory()
        identifier = 'link.%s.config' % self.link_name
        self.logger = self.logger_factory.getLogger('link.%s.config' % self.link_name)
        self.broker = MessageBroker('link:%s' % self.link_name)

    def set(self, key, value):
        return self.broker.set(key, value)

    def get(self, key):
        value = self.broker.get(key)
        # Do some typecasting
        if key in self.int_properties:
            value = int(value)
        if key in self.bool_properties:
            value = (value == 'True')
        
        return value

    def blocking_get(self, key):
        while True:
            value = self.get(key)
            if value is not None:
                self.logger.debug('Fetched (blocking) %s, got %s' % (key, value))
                return value
            time.sleep(0.1)
    
    def __getattr__(self, key):
        return self.get(key)

    def set_from_argparse(self, opts):
        """Given an optparse object from bin/openob, configure this link"""
        self.set("name", opts.link_name)
        if opts.mode == "tx":
            self.set("port", opts.port)
            self.set("jitter_buffer", opts.jitter_buffer)
            self.set("encoding", opts.encoding)
            self.set("bitrate", opts.bitrate)
            self.set("multicast", opts.multicast)
            self.set("input_samplerate", opts.samplerate)
            self.set("receiver_host", opts.receiver_host)
            self.set("opus_framesize", opts.framesize)
            self.set("opus_complexity", opts.complexity)
            self.set("opus_fec", opts.fec)
            self.set("opus_loss_expectation", opts.loss)
            self.set("opus_dtx", opts.dtx)

    def commit_changes(self, restart=False):
        """
            To be called after calls to set() on a running link to signal
            a reconfiguration event for that link. If restart is True, the link
            should simply terminate itself so it can be restarted with the new
            parameters. If restart is False, the link should set all parameters
            it can which do not involve a restart.
        """
        raise(NotImplementedError, "Link reconfiguration is not yet implemented")
