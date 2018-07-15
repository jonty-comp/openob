from openob.logger import LoggerFactory
from openob.broker import MessageBroker

class AudioInterface(object):

    """
        The AudioInterface class describes an audio interface on a Node.
        The configuration is not shared across the network. The type property of
        an AudioInterface should define the mode of link operation.
    """

    int_properties = ['samplerate']
    bool_properties = ['jack_auto']

    def __init__(self, interface_name):
        self.interface_name = interface_name
        self.logger_factory = LoggerFactory()
        self.logger = self.logger_factory.getLogger('audio.%s' % self.interface_name)
        self.broker = MessageBroker('audio:%s' % self.interface_name)

    def set(self, key, value):
        self.broker.set(key, value)

    def get(self, key):
        value = self.broker.get(key)
        if value == 'None':
            value = None
            
        if value is not None:
            # Do some typecasting
            if key in self.int_properties:
                value = int(value)
            if key in self.bool_properties:
                value = (value == 'True')
        return value

    def __getattr__(self, key):
        return self.get(key)

    def set_from_argparse(self, opts):
        """Set up the audio interface from argparse options"""
        if hasattr(opts, 'mode'):
            self.set("mode", opts.mode)

            if opts.mode == "tx":
                driver = opts.audio_input
                self.set("samplerate", opts.samplerate)
            elif opts.mode == "rx":
                driver = opts.audio_output
        else:
            driver = opts.audio_driver

        self.set('type', driver)

        if driver == "alsa":
            self.set("alsa_device", opts.alsa_device)
        elif driver == "jack":
            self.set("jack_auto", opts.jack_auto)
            if opts.jack_name is not None:
                self.set("jack_name", opts.jack_name)
            else:
                self.set("jack_name", "openob")
