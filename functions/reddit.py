import praw
import random

MAX_ENTRIES = 10 # max articles returned

class RedditManager:

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
        except requests.exceptions.HTTPError:
            retrieved_list.append("[REDDIT] %s is not a valid subject" % subject)
        finally:            
            return retrieved_list

