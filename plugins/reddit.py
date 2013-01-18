import sys
try:
    import praw
except ImportError, e:
    sys.stderr.write(e)
import random

MAX_ENTRIES = 10 # max articles returned

class RedditManager:

    """Manager for reddit entries. It's based on top of the Python Reddit API Wrapper"""

    def __init__(self):
        bot_user_agent = "pyircbot v0.1 by /u/sentenza github.com/zencoders/pyircbot"
        self.reddit = praw.UnauthenticatedReddit(user_agent=bot_user_agent)

    def retrieve_hot(self, subject="programming", num_entries=3, rand=False, nick=None):

        """ This method returns a list of num_entries hop articles OR a single pseudo-random top story 
        selected from the first top 100 entries """

        retrieved_list = list()
        try:
            topic = self.reddit.get_subreddit(subject)

            if not rand:
                # return num_entries articles
                submissions = topic.get_hot(limit=min(num_entries, MAX_ENTRIES))
                for single in submissions:
                    info = str(single)
                    retrieved_list.append(str(single) + "  " + str(single.short_link))
            elif nick is not None:
                #select a random set
                max_list = [story for story in topic.get_hot(limit=MAX_ENTRIES)]
                selected = random.choice(max_list)
                res = "%s: I am BOT, do not waste your time! Instead > " % nick
                retrieved_list.append(res + str(selected) + "  " + selected.short_link)
        except requests.exceptions.HTTPError, e:
            sys.stderr.write("HTTPError: %s\n" % e)
            retrieved_list.append("[REDDIT] %s is not a valid subject" % subject)
        finally:            
            if len(retrieved_list) == 0:
                retrieved_list.append("[Reddit] Nothing found for \"%s\" :(" % subject)
            return retrieved_list

