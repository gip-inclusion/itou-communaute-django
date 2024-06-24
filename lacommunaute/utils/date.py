from datetime import date

from dateutil.relativedelta import relativedelta


def get_last_sunday(theday=date.today()):
    days_to_subtract = (theday.weekday() + 1) % 7
    return theday - relativedelta(days=days_to_subtract)
