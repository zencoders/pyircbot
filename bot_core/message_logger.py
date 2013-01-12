import time

class MessageLogger(object):
    """
    Simple and independent logger class 
    """
    def __init__(self, logfile):
        self.logfile = logfile

    def log(self, message):
        timestamp = time.strftime("[%H:%M:%S]", time.localtime(time.time()))
        self.logfile.write('%s %s\n' % (timestamp, message))
        self.logfile.flush()

    def close(self):
        self.logfile.close()

