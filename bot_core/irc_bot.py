import time
import sys
import re
import random
from twisted.words.protocols import irc
from twisted.internet import threads, reactor

from message_logger import MessageLogger
from plugins.data_manager import DataManager
from plugins.karma_rate import KarmaRateLimiter
from plugins.welcome_machine import WelcomeMachine
from plugins.dice_roller import DiceRoller
from plugins.reddit import RedditManager

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
            sys.stderr.write("ERROR: %s\n" % error)
            sys.exit(1)
        self.logger = MessageLogger(logfile)
        self.logger.log(
            "[connected at %s]" %
            time.asctime(time.localtime(time.time()))
        )
        self.data_manager = DataManager(self.logger)
        self.karmrator = KarmaRateLimiter()
        self.reddit = RedditManager()
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
        goodbye_pattern = re.compile("(goodbye|bye|see you|see ya|see u)\s" + n + "(!|\s)?$", flags=re.IGNORECASE)
        bravo_pattern = re.compile("(bravo|great|good)\s" + n + "(!|\s)?$", flags=re.IGNORECASE)

        # TODO (sentenza) fix this check
        #ins = "([sf]uc|vaff|bastar|pezzo di m|coglio)"
        #insult_pattern = re.compile( ins+"(.*)"+n, re.IGNORECASE)

        #if insult_pattern.search(msg):
        #    self.msg(channel, "%s: jsc -e '{} + []'? HTH >> http://tiny.cc/watman" % user)
        #    vengeance = threads.deferToThread( self.data_manager.update_karma, user, plus=False, defense=-5 )
        #    vengeance.addCallback(self.threadSafeMsg)

        # Check if you are talking with BOT 
        if nickname_pattern.match(msg):
            deferred_reddit = threads.deferToThread(self.reddit.retrieve_hot, rand=True, nick=user)
            deferred_reddit.addCallback(self.threadSafeMsg)
        elif re.match(re.compile('[\w`]+\+\+$|[\w`]+--$', re.I), msg):
            self.karma_update(user, channel, msg)
        elif hello_pattern.match(msg):
            polite_msg = self.welcome_machine.ciao(user)
            self.msg(channel, polite_msg)
        elif goodbye_pattern.match(msg):
            self.msg(channel, "Hasta la vista, %s." % user)
        elif bravo_pattern.match(msg):
            self.msg(channel, "No hay problema %s ;)" % user)
        elif msg.startswith('!'):
            self.evaluate_command(user, channel, msg)


    def evaluate_command(self, user, channel, msg):

        """Command parser"""

        if self.factory.cm.verbose:
            # log commands
            self.logger.log("<%s> %s" % (user, msg))
            print "<%s> sends command: %s" % (user,msg)

        # dice command !roll NdF with Faces = 3|4|6|8|10|20
        dice_pattern = re.compile("!roll\s\d+d([3468]|10|20)$", flags = re.IGNORECASE)
        rand_pattern = re.compile("!rand\s\d+$", flags = re.IGNORECASE)
        reddit_pattern = re.compile("!reddit\s?(\d+|\d+\s\w+)?$", flags = re.IGNORECASE)
        msg_splits = msg.split()

        if re.match(re.compile("!(karma|k)(\s)*", re.IGNORECASE), msg):
            if len(msg_splits) == 1:
                fetch_word = user.lower()
            elif len(msg_splits) == 2:
                fetch_word = msg_splits[1].lower()
            else: # !karma first two etc
                return
            # Deferred call 
            deferred_fetch = threads.deferToThread(self.data_manager.fetch_karma, fetch_word)
            deferred_fetch.addCallback(self.threadSafeMsg)

        if re.match(re.compile("!(bestkarma|bk)(\s)*$", re.IGNORECASE), msg):
            deferred_best = threads.deferToThread(self.data_manager.get_karma_list)
            deferred_best.addCallback(self.threadSafeMsg)

        if re.match(re.compile("!(worstkarma|wk)(\s)*$", re.IGNORECASE), msg):
            deferred_worst = threads.deferToThread(self.data_manager.get_karma_list, desc_order=False)
            deferred_worst.addCallback(self.threadSafeMsg)

        if re.match(re.compile("!(bestwords|bw)(\s)*$", re.IGNORECASE), msg):
            deferred_bestw = threads.deferToThread(self.data_manager.get_karma_list, words=True)
            deferred_bestw.addCallback(self.threadSafeMsg)

        if re.match(re.compile("!(worstwords|ww)(\s)*$", re.IGNORECASE), msg):
            deferred_worstw = threads.deferToThread(self.data_manager.get_karma_list, desc_order=False, words=True)
            deferred_worstw.addCallback(self.threadSafeMsg)

        if re.match(re.compile("!(lastseen|ls)(\s)*", re.IGNORECASE), msg):
            if len(msg_splits) == 2:
                fetch_user = msg_splits[1].lower()
            else: # !karma first two etc
                return
            deferred_lastseen = threads.deferToThread(self.data_manager.user_seen, fetch_user)
            deferred_lastseen.addCallback(self.threadSafeMsg)

        elif dice_pattern.match(msg):
            deferred_roll = threads.deferToThread(DiceRoller.roll, msg)
            deferred_roll.addCallback(self.threadSafeMsg)

        elif reddit_pattern.match(msg):
            deferred_reddit = None
            if len(msg_splits) == 1:
                deferred_reddit = threads.deferToThread(self.reddit.retrieve_hot)
            elif len(msg_splits) == 2:
                deferred_reddit = threads.deferToThread(self.reddit.retrieve_hot, num_entries=int(msg_splits[1]))
            elif len(msg_splits) == 3:
                deferred_reddit = threads.deferToThread(self.reddit.retrieve_hot, num_entries=int(msg_splits[1]), subject=msg_splits[2])

            if deferred_reddit is not None:
                deferred_reddit.addCallback(self.threadSafeMsg)


        elif rand_pattern.match(msg):
            if len(msg_splits) == 2:
                self.msg(channel, "Random number: %d" % (random.randint(0, int(msg_splits[1]) )) )

        elif msg == "!randtime":
            self.msg(channel, "Random Hour:Minute  %d:%.2d" % (random.randint(0,23), random.randint(0,59)) )

        elif msg.startswith( ('!commands', '!help') ):
            if len(msg_splits) == 1:
                self.msg(channel, self._help_command() )
            elif len(msg_splits) == 2:
                self.msg(channel, self._help_command(msg_splits[1]) )
                

    def userJoined(self, user, channel):

        """Called when a user joins the channel (with a predetermined probability)"""
        
        deferred_recordseen = threads.deferToThread(self.data_manager.record_lastseen, user.lower())
        deferred_recordseen.addCallback(self.threadSafeMsg)

        ciao_msg = self.welcome_machine.ciao(user)
        if random.randint(1,100) <= self.factory.cm.greeting_probability:
            self.msg(channel, ciao_msg)


    def kickedFrom(self, channel, kicker, message):

         """Called when someone kick the bot from the channel"""

         # Karma vengeance first of all of course ^__^
         vengeance = threads.deferToThread( self.data_manager.update_karma, kicker, plus=False, defense=-10 )
         # Rejoin
         self.join(channel)
         vengeance.addCallback(self.threadSafeMsg)
         self.describe(channel, "is angry")


    def karma_update(self, user, channel, msg):

        """Try to modify the Karma for a given nickname"""

        receiver_nickname = msg[:-2].lower()
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
            deferred_update = threads.deferToThread(self.data_manager.update_karma, user, plus=False)
            return
        if msg.endswith('++'):
            deferred_update = threads.deferToThread(self.data_manager.update_karma, receiver_nickname, plus=True)
        if msg.endswith('--'):
            deferred_update = threads.deferToThread( self.data_manager.update_karma, receiver_nickname, plus=False)

        deferred_update.addCallback(self.threadSafeMsg)
        #self.msg(channel, self.data_manager.fetch_karma(receiver_nickname)) 
        self.logger.log("%s modified Karma: %s" % (user, receiver_nickname))


    def threadSafeMsg(self, message):

        """Thread-safe callback. Thread created by threads.deferToThread cannot just call 
        IRCClient.msg, since that method is not thread-safe."""

        # see https://github.com/zencoders/pyircbot/issues/3
        chan = "#" + self.factory.channel
        if type(message) is str:
            reactor.callFromThread(self.msg, chan , message)
        elif type(message) is list:
            for el in message:
                reactor.callFromThread(self.msg, chan , str(el))
                

    def get_current_timestamp(self):
        return time.asctime(time.localtime(time.time()))

    def _help_command(self, command=None):
        
        """This method returns the help message"""

        help_msg = "Valid commands: !help <command>, !commands, !karma [user], !roll Nd(3|4|6|8|10|20), !rand arg, !randtime,"
        help_msg += "!reddit [entries] [subject], !lastseen USER, !beskarma, !worstkarma, !bestwords, !worstwords"

        if command is not None:

            if command == "karma":
                help_msg = "!karma [user]: returns user's karma score. (Compact form: !k) "
                help_msg += "<user>++ or <user>-- to modify karma score of the specified user." 

            elif command == "roll":
                help_msg = "!roll NdN: roll dice (like D&D: d3, d4, d6, d8, d10, d20)"

            elif command == "rand":
                help_msg = "!rand returns randint(0, arg)"

            elif command == "randtime":
                help_msg = "!randtime returns a random 24h (HH:MM) timestamp"

            elif command == "reddit":
                help_msg = "!reddit [NUMBER] [SUBJECT] to retrieve the latest  NUMBER hot reddit news about SUBJECT, otherwise list the last 3 about computer programming"

            elif command == "lastseen":
                help_msg = "!lastseen USER returns the datetime of the last USER's join. Short form: !ls"

            elif command == "bestwords":
                help_msg = "!bestwords returns a list of the most karmed words. Short form: !bw"

            elif command == "worstwords":
                help_msg = "!worstwords returns a list of the worst karmed words. Short form: !ww"

            elif command == "bestkarma":
                help_msg = "!bestkarma returns a list of the most karmed users. Short form: !bk"

            elif command == "worstkarma":
                help_msg = "!worstkarma returns a list of the worst karmed users. Short form: !wk"

            else:
                help_msg = "%s is not a valid command!" % command

        return help_msg

