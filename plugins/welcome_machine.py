from interfaces.singleton import Singleton
import random

class WelcomeMachine:
    """Singleton class. 
    It randomly selects a greeting phrase from a static file"""
    # There is no need to call twice the constructor
    __metaclass__ = Singleton

    def __init__(self, greetings_file_path):
        self.welcomes = []
        # with take care of all the I/O for you
        with  open(greetings_file_path, 'r') as greetings_file:
            for line in greetings_file:
                self.welcomes.append(line)

    def ciao(self, nickname):
        """Say hi to nickname."""
        ave = random.choice(self.welcomes)
        if '%s' in ave:
            return (ave % nickname).rstrip()
