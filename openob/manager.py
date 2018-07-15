from gi.repository import GLib

from openob.logger import LoggerFactory
from openob.broker import MessageBroker
from openob.node import Node
from openob.link_config import LinkConfig
from openob.audio_interface import AudioInterface

class Manager(object):
    nodes = []

    def __init__(self, config_host, host_name):
        self.host_name = host_name
        self.logger_factory = LoggerFactory()
        self.logger = self.logger_factory.getLogger('manager.%s' % self.host_name)

        MessageBroker.setup(config_host, host_name)
        self.message_broker = MessageBroker('manager:%s' % self.host_name)

    def setup_from_argparse(self, opts):
        self.audio_input = AudioInterface('input')
        self.audio_input.set_from_argparse(opts)
        self.audio_input.mode = 'tx'

        self.audio_output = AudioInterface('output')
        self.audio_output.set_from_argparse(opts)
        self.audio_output.mode = 'rx'

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
                self.create_link(message[2], message[3])
            elif message[1] == 'destroy_link':
                self.destroy_link(message[2])
            elif message[1] == 'reconfigure_link':
                self.reconfigure_link(message[2])
            else:
                self.logger.error('Did not understand message type: %s' % message[1])
        else:
            self.logger.debug('Message not for this manager')

    def check_audio_interface(self, audio_interface):
        if audio_interface == self.audio_input.interface_name:
            return self.audio_input
        elif audio_interface == self.audio_output.interface_name:
            return self.audio_output
        else:
            # Unrecognised interface
            self.logger.exception('Unrecognised audio interface on this manager: %s' % audio_interface)
            return False

    def create_link(self, link_name, audio_interface):
        audio_interface = self.check_audio_interface(audio_interface)

        try:
            for node in self.nodes:
                if node.node_name == '%s_%s' % (audio_interface.interface_name, self.host_name):
                    raise Exception('%s is already assigned to a node' % audio_interface.interface_name)

            link_config = LinkConfig(link_name)
            self.logger.debug('Setting up new %s link %s' % (audio_interface.mode, link_name))
            node = Node('%s_%s' % (audio_interface.interface_name, self.host_name))
            
            if node.start_link(link_config, audio_interface):
                self.nodes.append(node)
        except Exception as e:
            self.logger.error('Error setting up link: %s' % e.message)

    def destroy_link(self, audio_interface):
        audio_interface = self.check_audio_interface(audio_interface)

        try:
            for node in self.nodes:
                if node.node_name == '%s_%s' % (audio_interface.interface_name, self.host_name):
                    self.logger.debug('Stopping node %s' % node.node_name)
                    node.stop_link()
                    self.nodes.remove(node)
                    return True
            self.logger.error('No link found for interface %s' % audio_interface.interface_name)
        except Exception as e:
            self.logger.error('Error destroying link: %s' % e.message)

    def reconfigure_link(self, link_name):
        # TODO: fetch link info based on specified link name and reconfigure parameters
        pass
        
