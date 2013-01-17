import time
import sys
import re
import random
from twisted.words.protocols import irc
from twisted.internet import threads, reactor

from message_logger import MessageLogger
from karma.karma_manager import KarmaManager
from karma.karma_rate import KarmaRateLimiter
from functions.welcome_machine import WelcomeMachine
from functions.dice_roller import DiceRoller

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


    def privmsg(self, user, channel, msg):

        """This will get called when the bot receives a message."""

        user = user.split('!', 1)[0]
        #words = msg.split()

        # QUERY BOT DIRECTLY
        if channel == self.nickname:
            msg = "It's useless to query this BOT. Consider using !help in #", self.factory.channel
            self.msg(user, msg)
            return

        # Otherwise check to see if it is a message directed at me
        n = self.nickname
        # pattern for matching the bot's nick
        nickname_pattern = re.compile(n + "(:|,)?\s", flags=re.IGNORECASE)
        hello_pattern = re.compile("(hi|hello|ciao|hola|aloha)\s" + n + "(!|\s)?$", flags=re.IGNORECASE)
        bravo_pattern = re.compile("(bravo|great)\s" + n + "(!|\s)?$", flags=re.IGNORECASE)

        # Check if you are talking with BOT 
        if nickname_pattern.match(msg):
            self.msg(channel, "%s: I am BOT, do not waste your time!" % user)
        elif msg.startswith('!'):
            self.evaluate_command(user, channel, msg)
        elif re.match(re.compile('\w+\+\+$|\w+--$'), msg):
            self.karma_update(user, channel, msg)
        elif hello_pattern.match(msg):
            polite_msg = self.welcome_machine.ciao(user)
            self.msg(channel, polite_msg)
        elif bravo_pattern.match(msg):
            self.msg(channel, "No hay problema %s ;)" % user)


    def evaluate_command(self, user, channel, msg):

        """Command parser"""

        if self.factory.cm.verbose:
            # log commands
            self.logger.log("<%s> %s" % (user, msg))
            print "<%s> sends command: %s" % (user,msg)

        # dice command !roll NdF with Faces = 3|4|6|8|10|20
        dice_pattern = re.compile("!roll\s\d+d([3468]|10|20)", flags = re.IGNORECASE)
        msg_splits = msg.split()

        # check for commands starting with bang!
        if msg.startswith('!karma'):
            
            if len(msg_splits) == 1:
                fetch_user = user
            elif len(msg_splits) == 2:
                fetch_user = msg_splits[1]
            else: # !karma first two etc
                return

            # self.msg(channel, self.karma_manager.fetch_karma(fetch_user)) 
            # Deferred call 
            deferred_fetch = threads.deferToThread(self.karma_manager.fetch_karma, nick=fetch_user)
            deferred_fetch.addCallback(self.threadSafeMsg)

        elif dice_pattern.match(msg):
            deferred_roll = threads.deferToThread(DiceRoller.roll, msg)
            deferred_roll.addCallback(self.threadSafeMsg)

        elif msg == "!randtime":
            self.msg(channel, "Random Hour:Minute  %d:%.2d" % (random.randint(0,23), random.randint(0,59)) )

        elif msg.startswith( ('!commands', '!help') ):
            if len(msg_splits) == 1:
                self.msg(channel, self._help_command() )
            elif len(msg_splits) == 2:
                self.msg(channel, self._help_command(msg_splits[1]) )
                

    def userJoined(self, user, channel):

        """Called when a user joins the channel (with a predetermined probability)"""

        ciao_msg = self.welcome_machine.ciao(user)
        if random.randint(1,100) <= self.factory.cm.greeting_probability:
            self.msg(channel, ciao_msg)


    def kickedFrom(self, channel, kicker, message):

         """Called when someone kick the bot from the channel"""

         # Karma vengeance first of all of course ^__^
         vengeance = threads.deferToThread( self.karma_manager.update_karma, kicker, plus=False, defense=-10 )
         # Rejoin
         self.join(channel)
         vengeance.addCallback(self.threadSafeMsg)
         self.describe(channel, "is angry")


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
            deferred_update = threads.deferToThread(self.karma_manager.update_karma, user, plus=False)
            return
        if msg.endswith('++'):
            deferred_update = threads.deferToThread(self.karma_manager.update_karma, receiver_nickname, plus=True)
        if msg.endswith('--'):
            deferred_update = threads.deferToThread( self.karma_manager.update_karma, receiver_nickname, plus=False)

        deferred_update.addCallback(self.threadSafeMsg)
        #self.msg(channel, self.karma_manager.fetch_karma(receiver_nickname)) 
        self.logger.log("%s modified Karma: %s" % (user, receiver_nickname))


    def threadSafeMsg(self, message):

        """Thread-safe callback. Thread created by threads.deferToThread cannot just call 
        IRCClient.msg, since that method is not thread-safe."""

        # see https://github.com/zencoders/pyircbot/issues/3
        chan = "#" + self.factory.channel
        reactor.callFromThread(self.msg, chan , message)

    def get_current_timestamp(self):
        return time.asctime(time.localtime(time.time()))

    def _help_command(self, command=None):
        
        """This method returns the help message"""

        help_msg = "Valid commands: !help <command>, !commands, !karma [user], !roll Nd(3|4|6|8|10|20), !randtime"
        if command is not None:

            if command == "karma":
                help_msg = "!karma [user]: returns user's karma score.  "
                help_msg += "<user>++ or <user>-- to modify karma score of the specified user." 

            elif command == "roll":
                help_msg = "!roll NdN: roll dice (like D&D: d2, d4, d6, d8, d10, d20)"

            elif command == "randtime":
                help_msg = "!randtime returns a random 24h (HH:MM) timestamp"

            else:
                help_msg = "%s is not a valid command!" % command

        return help_msg

