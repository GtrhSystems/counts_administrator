
import datetime


def CalculateDateLimit(date, months) :


    days = months * 30
    date_limit = date + datetime.timedelta(days=days)
    return  date_limit



def getDifference(then, now, interval="secs"):
    duration = now - then
    duration_in_s = duration.total_seconds()

    # Date and Time constants
    yr_ct = 365 * 24 * 60 * 60  # 31536000
    day_ct = 24 * 60 * 60  # 86400
    hour_ct = 60 * 60  # 3600
    minute_ct = 60

    def yrs():
        return divmod(duration_in_s, yr_ct)[0]

    def days():
        return divmod(duration_in_s, day_ct)[0]

    def hrs():
        return divmod(duration_in_s, hour_ct)[0]

    def mins():
        return divmod(duration_in_s, minute_ct)[0]

    def secs():
        return duration_in_s

    return {
        'yrs': int(yrs()),
        'days': int(days()),
        'hrs': int(hrs()),
        'mins': int(mins()),
        'secs': int(secs())
    }[interval]