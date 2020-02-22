import os
from datetime import datetime
from dateutil import tz, parser
from pytz import timezone

LOCAL_TIMEZONE = timezone(os.environ['LOCAL_TZ'])
UTC_TIMEZONE = tz.UTC

def local_day_start():
    dt = datetime.now(LOCAL_TIMEZONE)
    return datetime(dt.year, dt.month, dt.day, tzinfo=LOCAL_TIMEZONE)

def to_utc(dt):
    if dt.tzinfo is None:
        return dt.replace(tzinfo=tz.tzlocal()).astimezone(tz.UTC)
    else:
        return dt.astimezone(tz.UTC)

def utcnow():
    return datetime.now(UTC_TIMEZONE)

def to_string(dt):
    return to_utc(dt).strftime('%Y-%m-%dT%H:%M:%SZ')

def from_string(s):
    dt = parser.parse(s)
    return to_utc(dt)
