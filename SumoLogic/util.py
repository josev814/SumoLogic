from .constants import TIME_SPEC_LOOKUP
from .regex import TIME_SPEC_REGEX


def is_true(s):
    if s is True or s.lower() in ('1', 't', 'true', 'y', 'yes'):
        return True
    return False


def is_false(s):
    return not is_true(s)


def get_time_spec(timestr):
    m = TIME_SPEC_REGEX.search(timestr)

    if not m or 'units' not in m.groupdict() or 'period' not in m.groupdict() or m.group('units') == '':
        raise Exception("Invalid time specification: string format error: %s", timestr)

    units = int(m.group('units'))
    period = m.group('period') or 's'  # seconds is the default

    return units, period


def calculate_seconds(timestr, zero_ok=False):
    # return the number of seconds in a given timestr such as 1d (1 day),
    # 13w (13 weeks), 5s (5seconds), etc...
    if type(timestr) is int:
        return timestr

    units, period = get_time_spec(timestr)

    if units == 0 and not zero_ok:
        raise Exception("Invalid time specification: units = 0")

    seconds = units * TIME_SPEC_LOOKUP[period]
    return seconds


def normalize_whitespace(string):
    return ' '.join(string.split())

