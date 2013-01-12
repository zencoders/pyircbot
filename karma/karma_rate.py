import time
from collections import defaultdict

class KarmaRateLimiter(object):

    def __init__(self, timeout=3600):
        """timeout in seconds - default 1 h"""
        self.timeout = timeout
        # http://goo.gl/ZFmFX
        # http://stackoverflow.com/a/5900628
        self.user_last_request = defaultdict(int)

    def is_rate_limited(self, nick):
        now = int(time.time())
        if nick not in self.user_last_request:
            self.user_last_request[nick] = now
            return False
        elif (now - self.user_last_request[nick]) < self.timeout:
            return True
        else:
            self.user_last_request[nick] = now
            return False

    def user_timeout(self, nick):
        """Return the user specific timeout"""
        if nick not in self.user_last_request:
            return 0
        else:
            wait_time = self.timeout - (int(time.time()) - self.user_last_request[nick])
            return wait_time
