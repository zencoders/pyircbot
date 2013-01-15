import time
from collections import defaultdict

class KarmaRateLimiter(object):

    def __init__(self, timeout=360, penalty=3):
        """timeout in seconds - default 6 min"""
        self.timeout = timeout
        self.penalty = penalty
        # http://goo.gl/ZFmFX
        # http://stackoverflow.com/a/5900628
        self.user_last_request = defaultdict(lambda:[int, int])
        # defaultdict needs callable obj

    def rate_limit(self, nick):
        """Return 0 if not rate_limited, 1 if has penalization, 2 otherwise"""
        now = int(time.time())
        if nick not in self.user_last_request:
            self.user_last_request[nick] = [now,0]
            return 0
        elif (now - self.user_last_request[nick][0]) < self.timeout:
            # Timeout not expired, so increase the counter
            self.user_last_request[nick][1] += 1
            # User is rate limited
            if self.user_last_request[nick][1] % self.penalty == 0:
                # give him the penalization!
                return 1
            else:
                return 2
        else:
            # > timeout OK
            self.user_last_request[nick] = [now, 0]
            return 0

    def user_timeout(self, nick):
        """Return the user specific timeout"""
        if nick not in self.user_last_request:
            return 0
        else:
            wait_time = self.timeout - (int(time.time()) - self.user_last_request[nick][0])
            return wait_time
