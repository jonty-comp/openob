from openob.logger import LoggerFactory
from openob.broker import MessageBroker
from openob.audio_interface import AudioInterface

class Manager(object):
    def __init__(self, config_host, host_name):
        self.host_name = host_name
        self.logger_factory = LoggerFactory()
        self.logger = self.logger_factory.getLogger('manager.%s' % self.host_name)

        MessageBroker.setup(config_host, host_name)
        self.message_broker = MessageBroker('manager:%s' % self.host_name)
        pass

    def setup_from_argparse(self, opts):
        self.audio_input = AudioInterface('input')
        self.audio_input.set_from_argparse(opts)

        self.audio_output = AudioInterface('output')
        self.audio_output.set_from_argparse(opts)


    def run(self):
        self.logger.info('Waiting for configuration from config server...')
        # TODO: implement configuration fetching/listening from redis