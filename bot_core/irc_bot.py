import time
import sys
import re
import random
from twisted.words.protocols import irc

from message_logger import MessageLogger
from karma.karma_manager import KarmaManager
from karma.karma_rate import KarmaRateLimiter
from functions.welcome_machine import WelcomeMachine

class IRCBot(irc.IRCClient):
    """Python Twisted IRC BOT. irc.IRCClient specialization."""
    
    def _get_nickname(self):
        return self.factory.nickname
    nickname = property(_get_nickname)

    def _help_command(self, command=None):
        help_msg = "Valid commands: !help <command>, !commands, !karma"
        if command is not None:
            if command == "karma":
                help_msg = "!karma [user]: returns user's karma score.  "
                help_msg += "<user>++ or <user>-- to modify karma score of the specified user." 
            else:
                help_msg = "%s is not a valid command!" % command
        return help_msg

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
        self.karma_manager = KarmaManager()
        self.karmrator = KarmaRateLimiter()
        # Singleton WelcomeMachine class
        self.welcome_machine = WelcomeMachine(self.factory.cm.greetings_file_path)

    def connectionLost(self, reason):
        irc.IRCClient.connectionLost(self, reason)
        self.logger.log("[disconnected at %s]" % self.get_current_timestamp() )
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
        
        if channel == self.nickname:
            msg = "It's useless to query this BOT. Consider using !help in #", self.factory.channel
            self.msg(user, msg)
            return

        # Otherwise check to see if it is a message directed at me
        n = self.nickname
        # Check if you are talking with me, like BOT: <msg> || BOT, <msg> || BOT <msg>
        if msg.startswith((n + ":", n + ",", n)):
            msg = "%s: I am BOT, do not waste your time!" % user
            self.msg(channel, msg)
            self.logger.log("<%s> %s" % (self.nickname, msg))
        elif msg.startswith('!'):
            self.evaluate_command(user, channel, msg)
        #elif msg.endswith( ("++","--") ):
        elif re.match(re.compile('\w+\+\+|\w+--'), msg):
            self.karma_update(user, channel, msg)

    def evaluate_command(self, user, channel, msg):
        if self.factory.cm.verbose:
            print "<%s> sends command: %s" % (user,msg)
        msg_splits = msg.split()
        # check for commands starting with bang!
        if msg.startswith('!karma'):
            if len(msg_splits) == 1:
                fetch_user = user
            elif len(msg_splits) == 2:
                fetch_user = msg_splits[1]
            else: return
            self.msg(channel, self.karma_manager.fetch_karma(fetch_user)) 
        elif msg.startswith( ('!commands', '!help') ):
            if len(msg_splits) == 1:
                self.msg(channel, self._help_command() )
            elif len(msg_splits) == 2:
                self.msg(channel, self._help_command(msg_splits[1]) )
                
    def userJoined(self, user, channel):
        """Called when a user joins the channel (10% chance)"""
        ciao_msg = self.welcome_machine.ciao(user)
        if random.randint(1,100) <= self.factory.cm.greeting_probability:
            self.msg(channel, ciao_msg)

    def karma_update(self, user, channel, msg):
        """Try to modify the Karma for a given nickname"""
        receiver_nickname = msg[:-2]
        if receiver_nickname == user:
            self.msg(channel, "%s: you can't alter your own karma!" % user)
            return
        limit = self.karmrator.rate_limit(user)
        if  limit == 2:
            waiting_minutes = self.karmrator.user_timeout(user)
            self.msg(user, "%s: you have to wait %s sec for your next karmic request!" % (user, waiting_minutes))
            return
        if limit == 1:
            # Penalize User
            self.msg(channel, "%s: I warned you... Now you have lost karma. :(" % user )
            self.karma_manager.update_karma(user, plus=False)
            return
        if msg.endswith('++'):
            self.karma_manager.update_karma(receiver_nickname, plus=True)
        if msg.endswith('--'):
            self.karma_manager.update_karma(receiver_nickname, plus=False)
        self.msg(channel, self.karma_manager.fetch_karma(receiver_nickname)) 
        self.logger.log("%s modified Karma: %s" % (user, receiver_nickname))

    def get_current_timestamp(self):
        return time.asctime(time.localtime(time.time()))
