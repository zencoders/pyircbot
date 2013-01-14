import os
from twisted.internet import protocol, reactor
from irc_bot import IRCBot
from config import ConfigManager

class BotFactory(protocol.ClientFactory):
    """
    A ClientFactory for BasicIRCbot.
    """

    def __init__(self):
        self.cm = ConfigManager()
        self.channel = self.cm.channel
        self.protocol = IRCBot
        # The factory needs the protocol class to make a new connection
        self.nickname = self.cm.bot_nick
        if not os.path.exists(self.cm.data_path):
            os.makedirs(self.cm.data_path)
        self.data_folder = self.cm.data_path
        self.log_filename = self.data_folder + self.nickname + ".log"


    def connect(self):
        """Connect the factory to the host/port and pass the factory itself"""
        address = self.cm.server_address
        port = self.cm.server_port
        print "Connecting to %s:%s" % (address,  port)
        reactor.connectTCP(address, port, self)

    def clientConnectionLost(self, connector, reason):
        """If we get disconnected, reconnect to server."""
        print "Lost connection (%s), reconnecting." % (reason,)
        connector.connect()

    def clientConnectionFailed(self, connector, reason):
        print "Could not connect:", reason
        reactor.stop()

    def run(self):
        """Run the bot"""
        reactor.run()
