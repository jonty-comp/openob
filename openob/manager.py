from gi.repository import GLib

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
        self.logger.info('Listening for configuration from config server...')
        self.main_loop = GLib.MainLoop()
        self.message_broker.subscribe('events', self.on_message)

        GLib.timeout_add(100, self.message_broker.check_messages)

        self.main_loop.run()

    def on_message(self, message):
        self.logger.debug('New message on events channel: %s' % message['data'])
        message = message['data'].split(',')

        if message[0] == self.host_name:
            if message[1] == 'create_link':
                self.create_link(message[2])
            elif message[2] == 'destroy_link':
                self.destroy_link(message[2])
            elif message[2] == 'reconfigure':
                self.reconfigure_link(message[3])
            else:
                self.logger.error('Did not understand message type: %s' % message[1])
        else:
            self.logger.debug('Message not for this manager')

    def create_link(self, audio_interface):
        # TODO: fetch link info based on specified audio interface and set up link
        pass

    def destroy_link(self, audio_interface):
        # TODO: fetch link info based on specified audio interface and destroy link
        pass

    def reconfigure_link(self, link_name):
        # TODO: fetch link info based on specified link name and reconfigure parameters
        pass
        
