import os
from twisted.internet import protocol, reactor
from irc_bot import IRCBot

class BotFactory(protocol.ClientFactory):
    """
    A ClientFactory for BasicIRCbot.
    """

    # The factory needs the protocol class to make a new connection

    def __init__(self, channel, nickname, log_folder):
        self.channel = channel
        self.protocol = IRCBot
        self.nickname = nickname
        if not os.path.exists(log_folder):
            os.makedirs(log_folder)
        self.log_filename = log_folder + self.nickname + ".log"

    def connect(self, server_address, port):
        """Connect the factory to the host/port and pass the factory itself"""
        print "Connecting to %s:%s" % (server_address,  port)
        reactor.connectTCP(server_address, port, self)

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
