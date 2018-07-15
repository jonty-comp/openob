import sys
import time
from openob.logger import LoggerFactory
from openob.rtp.tx import RTPTransmitter
from openob.rtp.rx import RTPReceiver
from openob.link_config import LinkConfig

class Node(object):

    """
        OpenOB node instance.

        Nodes run links. Each Node looks after its end of a link, ensuring
        that it remains running and tries to recover from failures, as well as
        responding to configuration changes.

        Nodes have a name; everything else is link specific.

        For instance, a node might be the 'studio' node, which would run a
        'tx' end for the 'stl' link.

        Nodes have a config host which is where they store their inter-Node
        data and communicate with other Nodes.
    """

    def __init__(self, node_name):
        """Set up a new node."""
        self.node_name = node_name
        self.logger_factory = LoggerFactory()
        self.logger = self.logger_factory.getLogger('node.%s' % self.node_name)

    def start_link(self, link_config, audio_interface):
        """
          Start a new TX or RX node.
        """
        self.logger.info("Link %s initial setup start on %s" % (link_config.link_name, self.node_name))
        mode = audio_interface.mode
        try:
            if mode == 'tx':
                try:
                    self.logger.info("Starting up transmitter")
                    transmitter = RTPTransmitter(self.node_name, link_config, audio_interface)
                    transmitter.run()
                    caps = transmitter.get_caps()
                    self.logger.debug("Got caps from transmitter, setting config")
                    link_config.set("caps", caps)
                    self.active_link = transmitter
                    return True
                except Exception as e:
                    self.logger.exception("Transmitter crashed for some reason!")
            elif mode == 'rx':
                self.logger.info("Waiting for transmitter capabilities...")
                caps = link_config.blocking_get("caps")
                self.logger.info("Got caps from transmitter")
                try:
                    self.logger.info("Starting up receiver")
                    receiver = RTPReceiver(self.node_name, link_config, audio_interface)
                    receiver.run()
                    self.active_link = receiver
                    return True
                except Exception as e:
                    self.logger.exception("Receiver crashed for some reason!")
            else:
                self.logger.critical("Unknown audio interface mode (%s)!" % mode)
                sys.exit(1)
        except Exception as e:
            self.logger.exception("Unknown exception thrown - please report this as a bug! %s" % e)
            raise
    
    def stop_link(self):
        if self.active_link is None:
            raise Exception('Node not active')
        else:
            self.active_link.stop()

    def loop(self):
        """
            Run the mainloop for a single link
        """
        if self.active_link is None:
            raise Exception('There is no active link')
        
        self.active_link.loop()
