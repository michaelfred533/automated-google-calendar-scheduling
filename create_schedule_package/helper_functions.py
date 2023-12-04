"""
contains general helper functions
"""
import datetime
import pytz

def create_timezone_datetime_object(time_ISO_string: str) -> datetime.datetime:
    """
    converts a time in string format into a datetime object w/ timezone to be used to compare with other datetime objects
    """
    
    date = datetime.datetime.today().date()
    datetime_string = str(date) + time_ISO_string
    naive_datetime_object = datetime.datetime.strptime(datetime_string, '%Y-%m-%dT%H:%M:%S')
    timezone_datetime_object = pytz.timezone('America/Los_Angeles').localize(naive_datetime_object)

    return timezone_datetime_object