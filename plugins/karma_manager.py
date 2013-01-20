import time
import sqlite3
import sys
import unicodedata as ud
from config import ConfigManager
from contextlib import closing

# TODO (sentenza) refactoring needed - DataManager ?
class KarmaManager():

    def __init__(self, irc_logger):
        self.conf = ConfigManager()
        self.db_path = self.conf.data_path + "data.sqlite"
        self.users_table = "users"
        self.karma_table = "karma"
        self.create_karma_table()
        self.create_users_table()
        # TODO (sentenza) Logger.getLogger or Twisted.logger
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


    def strip_nonascii(self, s):
        """This method remove non-ascii chars from argument"""
        return ud.normalize('NFKD', unicode(s) ).encode('ascii','ignore')


    @db_commit
    def create_users_table(self, cursor):

        """ Check the existence of the users log table, otherwise create it """

        cursor.execute("""
                        CREATE TABLE IF NOT EXISTS %s  (
                        user text PRIMARY KEY,
                        lastseen INTEGER NOT NULL
                    )
                    """ % self.users_table )


    @db_commit
    def create_karma_table(self, cursor):

        """ Check the existence of the karma log table, 
        otherwise create it """

        cursor.execute("""
                        CREATE TABLE IF NOT EXISTS %s  (
                        time INTEGER NOT NULL,
                        word TEXT PRIMARY KEY,
                        score INTEGER
                    )
                    """ % self.karma_table )

    @db_commit 
    def fetch_karma(self, cursor, word):
        
        """Returns a message with the value of Karma for a specific word"""

        word = self.strip_nonascii(word)
        cursor.execute("SELECT score FROM %s WHERE word=?" % self.karma_table, (word,))
        karma_score = cursor.fetchone()
        if karma_score is None:
            return "Karma is inscrutable for %s" % word
        return "%s: %s" % (word, karma_score[0])


    @db_commit
    def update_karma(self, cursor, word, plus=True, defense=0):

        """Updates the karma value of a given word"""
        
        word = self.strip_nonascii(word)

        if defense == 0:
            score = 1 if plus else -1
        else:
            score = defense

        timestamp = int(time.time())
        cursor.execute("""
            UPDATE %s SET time=?, score=(score + ?) WHERE word=?
            """ % self.karma_table, (timestamp, score, word))
        if cursor.rowcount != 1:
            cursor.execute("""
                INSERT INTO %s values (?,?,?)
                """ % self.karma_table, (timestamp, word, score))
        verb = "blesses" if plus else "hits"

        if defense == -10: # after a kick
            verb = "DREADFULLY hits"
        elif defense == -5: # after someone's kicked (spadaccio)
            verb = "heavily hits"

        return "Karma %s %s" % (verb, word)


    @db_commit
    def record_lastseen(self, cursor, user):

        """This method insert or update a user's lastseen timestamp"""

        nick = self.strip_nonascii(user)
        timestamp = int(time.time())
        cursor.execute("UPDATE %s SET lastseen=? WHERE user=?" % self.users_table, (timestamp, nick))
        if cursor.rowcount != 1:
            cursor.execute("INSERT INTO %s values (?,?)" % self.users_table, (user, timestamp))


    @db_commit
    def user_seen(self, cursor, user):

        """ Returns a string with the lastseen timestamp of the given user """

        nick = self.strip_nonascii(user)
        cursor.execute("SELECT lastseen FROM %s WHERE user=?" % self.users_table, (user,))
        lastseen = cursor.fetchone()
        if lastseen is None:
            return "I've never seen %s before. And you?" % user
        return "%s was seen: %s" % (user, time.ctime(lastseen[0]))

    @db_commit
    def get_users_karma(self, cursor, limit=5, desc_order=True):

        """Get a list of LIMIT karma values about words recognized as user"""

        order = "DESC" if desc_order else "ASC"
        cursor.execute("""SELECT k.word, k.score FROM karma AS k
                        INNER JOIN users AS u
                        ON k.word=u.user
                        ORDER BY k.score %s
                        LIMIT %d""" % (order, limit) )

        users_karma = cursor.fetchall()
        if users_karma is None:
            return ["There is no information about users' karma",]
        else:
            karma_list = list()
            for row in users_karma:
                karma_list.append(str(row[0]) + ": " + str(row[1]))
            return karma_list

