import datetime


def datestamp():
    """Return a datestamp string in the format YYYYMMDDHHMMSS"""
    return datetime.datetime.now().strftime("%Y%m%d%H%M%S")


def dateparse(datestring):
    """Return a datetime object from a datestamp string in the format YYYYMMDDHHMMSS"""
    return datetime.datetime.strptime(datestring, "%Y%m%d%H%M%S")