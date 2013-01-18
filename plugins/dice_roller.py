import random

MAX_ROLLS = 1000

class DiceRoller(object):

    """D&D style dice roller"""

    @classmethod
    def roll(cls, message, faces = 6):

        """ Roll a dice with a command like 4d6 (4 rolls of a d6 dice) """
        try:
            # message matched re: !roll\s\d+d([3468]|10|20)
            message = message.split() # now message[1] is [0-9]+d[0-9]+
            numbers = message[1].lower().split('d')
            repetitions = min(int(numbers[0]), MAX_ROLLS)
            faces = int(numbers[1])
        except Exception, e:
            # TODO (sentenza) logger
            print e
            return "ERROR: " + e

        result = sum([random.randint(1, faces) for _ in xrange(repetitions)])

        return "I threw %d d%d. The result is: %d" % (repetitions, faces, result)
