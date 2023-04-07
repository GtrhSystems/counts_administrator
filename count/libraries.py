
import datetime


def CalculateDateLimit(months) :


    days = months * 30
    date_limit = datetime.datetime.now() + datetime.timedelta(days=days)
    return  date_limit