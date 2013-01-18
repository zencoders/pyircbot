import time
import sqlite3
import sys
import unicodedata as ud
from config import ConfigManager
from contextlib import closing

class KarmaManager():

    def __init__(self, irc_logger):
        self.conf = ConfigManager()
        self.db_path = self.conf.data_path + "karma.sqlite"
        self.karma_table = "karma"
        self.create_table()
        self.irc_logger = irc_logger
        

    def db_commit(method):

        """Decorator method for managing DB connection, commit, and close"""

        # closure
        def inner_procedure(self, *args, **kwargs):
            # Check the DB file
            try:
                with closing( sqlite3.connect(self.db_path) ) as connection:
                    cursor = connection.cursor()

                    # Calling the decorated method
                    result = method(self, cursor, *args, **kwargs)

                    connection.commit()
                    cursor.close()
                    return result

            except Exception, e: # Can't connect
                err_str = "SQLite3 error: %s\n" % e
                sys.stderr.write(err_str)
                self.irc_logger.log(err_str)
                return "DATABASE ERROR"


        return inner_procedure


    @db_commit
    def create_table(self, cursor):
        """ Check the existence of the karma log table, 
        otherwise create it """

        cursor.execute("""
                        CREATE TABLE IF NOT EXISTS %s  (
                        time INTEGER NOT NULL,
                        nick text PRIMARY KEY,
                        score integer
                    )
                    """ % self.karma_table )


    @db_commit 
    def fetch_karma(self, cursor, nick=None):
        
        """Returns a message with the value of Karma for a specific user (fetched by his nickname)"""

        if nick:
            nick = self.strip_nonascii(nick)
            cursor.execute("SELECT score FROM %s WHERE nick=?" % self.karma_table, (nick,))
            karma_score = cursor.fetchone()
            if karma_score is None:
                return "Karma is inscrutable for %s" % nick
            return "%s: %s" % (nick, karma_score[0])


    @db_commit
    def update_karma(self, cursor, nick, plus=True, defense=0):

        """Updates the karma value of a user via his nickname"""
        
        nick = self.strip_nonascii(nick)

        if defense == 0:
            score = 1 if plus else -1
        else:
            score = defense

        timestamp = int(time.time())
        cursor.execute("""
            UPDATE %s SET time=?, score=(score + ?) WHERE nick=?
            """ % self.karma_table, (timestamp, score, nick))
        if cursor.rowcount != 1:
            cursor.execute("""
                INSERT INTO %s values (?,?,?)
                """ % self.karma_table, (timestamp, nick, score))
        verb = "blesses" if plus else "hits"

        if defense == -10: # after a kick
            verb = "DREADFULLY hits"
        elif defense == -5: # after someone's kicked (spadaccio)
            verb = "heavily hits"

        return "Karma %s %s" % (verb, nick)

    def strip_nonascii(self, s):

        """This method remove non-ascii chars from argument"""

        return ud.normalize('NFKD', unicode(s) ).encode('ascii','ignore')
