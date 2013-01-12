import time
import sys
from twisted.words.protocols import irc

from message_logger import MessageLogger

class IRCBot(irc.IRCClient):
    """Python Twisted IRC BOT. irc.IRCClient specialization."""
    
    def _get_nickname(self):
        return self.factory.nickname
    nickname = property(_get_nickname)

    def connectionMade(self):
        irc.IRCClient.connectionMade(self)
        try:
            logfile = open(self.factory.log_filename, "a")
        except IOError, error:
            sys.exit(error)
        self.logger = MessageLogger(logfile)
        self.logger.log(
            "[connected at %s]" %
            time.asctime(time.localtime(time.time()))
        )

    def connectionLost(self, reason):
        irc.IRCClient.connectionLost(self, reason)
        self.logger.log(
            "[disconnected at %s]" %
            time.asctime(time.localtime(time.time()))
        )
        self.logger.close()

    # TODO (sentenza) ConfigManager password
    def identify(self):
        if self.password:
            self.msg('NickServ', 'RELEASE %s %s' % (self.nickname, self.password))
            self.msg('NickServ', 'RELEASE %s %s' % (self.nickname, self.password))
            self.msg('NickServ', 'IDENTIFY %s %s' % (self.nickname, self.password))

    def signedOn(self):
        """Called when bot has succesfully signed on to server."""
        self.join(self.factory.channel)
        self.identify()

    def action(self, user, channel, msg):
        """This will get called when the bot sees someone do an action."""
        # e.g. /me <action>
        user = user.split('!', 1)[0]
        self.logger.log("* %s %s" % (user, msg))

    def privmsg(self, user, channel, msg):
        """This will get called when the bot receives a message."""
        user = user.split('!', 1)[0]
        self.logger.log("<%s> %s" % (user, msg))
        
        # Check to see if they're sending me a private message
        if channel == self.nickname:
            msg = "It isn't nice to whisper!  Play nice with the group."
            self.msg(user, msg)
            return

        # Otherwise check to see if it is a message directed at me
        n = self.nickname
        # Check if you are talking with me, like BOT: <msg> || BOT, <msg> || BOT <msg>
        if msg.startswith((n + ":", n + ",", n)):
            msg = "%s: I am BOT, do not waste your time!" % user
            self.msg(channel, msg)
            self.logger.log("<%s> %s" % (self.nickname, msg))
