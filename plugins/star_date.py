from datetime import datetime
from datetime import date
import time
import calendar

# Test with http://www.hillschmidt.de/gbr/sternenzeit.htm

# Constants

K_NORMAL = 3.170979 * (10**-5)
# LEAP YEARS
K_LEAP = 3.162315 * (10**-5)
# it could be also 2161 (birth of the United Planet Federation) or 2323
FOUNDATION_YEAR = 2323
MEAN_DAYS_IN_YEAR = 365.2425

class StarDate(object):
    ''' Star Trek star date generator '''

    @staticmethod
    def current_stardate():
        '''Returns the current stardate (float) in the classic Star Trek format'''
        # UTC datetime.now()
        now = datetime.fromtimestamp(time.mktime(time.localtime()))
        earth_date = date(now.year,1,1)
        # delta from the first day of the year
        delta = now.date() - earth_date
        # Find if this year is leap
        k = K_NORMAL if not calendar.isleap(now.year) else K_LEAP
        # Computing star date
        first = (now.year - FOUNDATION_YEAR) + (delta.days / MEAN_DAYS_IN_YEAR)
        second = now.hour * 3600 + now.minute * 60 + now.second
        stardate = first * 1000 + second * k
        # Return a stardate with only two decimal digits
        return "Captain's log, stardate %.2f." % stardate

if __name__ == "__main__":
    print StarDate.current_stardate()
        


