import time
import sqlite3

class KarmaManager():

    def __init__(self, data_folder):
        self.db_path = data_folder + "karma.sqlite"
        # TODO (sentenza) use ConfigManager instead
        self.karma_table = "karma"
        self.create_table()

    def db_commit(method):
        """Decorator that manage DB connection, commit, and close"""
        # closure
        def inner_procedure(self, *args, **kwargs):
            connection = sqlite3.connect(self.db_path)
            cursor = connection.cursor()
            # Calling the decorated method
            result = method(self, cursor, *args, **kwargs)
            connection.commit()
            cursor.close()
            return result
        return inner_procedure

    @db_commit
    def create_table(self, cursor):
        # Check the existence of the karma log table
        cursor.execute("""
                        CREATE TABLE IF NOT EXISTS %s  (
                        time INTEGER NOT NULL,
                        nick text PRIMARY KEY,
                        score integer
                    )
                    """ % self.karma_table )

    @db_commit 
    def fetch_karma(self, cursor, nick=None):
        """Return the value of Karma for a specific user"""
        if nick:
            cursor.execute("SELECT score FROM %s WHERE nick=?" % self.karma_table, (nick,))
            karma_score = cursor.fetchone()
            if not karma_score:
                return "Karma is inscrutable for %s" % nick
            else:
                return "%s has karma of %s" % (nick, karma_score[0])

    @db_commit
    def update_karma(self, cursor, nick, plus=True):
        score = 1 if plus else -1
        timestamp = int(time.time())
        cursor.execute("""
            UPDATE %s SET time=?, score=(score + ?) WHERE nick=?
            """ % self.karma_table, (timestamp, score, nick))
        if cursor.rowcount != 1:
            cursor.execute("""
                INSERT INTO %s values (?,?,?)
                """ % self.karma_table, (timestamp, nick, score))


