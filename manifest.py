import datetime
from collections import namedtuple


Manifest = namedtuple('Manifest', 'code datetime')


def month_str_to_month(month_str):
    if month_str == 'January':   return 1
    if month_str == 'February':  return 2
    if month_str == 'March':     return 3
    if month_str == 'April':     return 4
    if month_str == 'May':       return 5
    if month_str == 'June':      return 6
    if month_str == 'July':      return 7
    if month_str == 'August':    return 8
    if month_str == 'September': return 9
    if month_str == 'October':   return 10
    if month_str == 'November':  return 11
    if month_str == 'December':  return 12
    raise Exception(f"{month_str} isn't real!")


def parse_datetime(part):
    datetime_str, ago_id = part.split('UTC')
    datetime_str = datetime_str.strip()
    day_str, month_str, year_str, _, time_str = datetime_str.split(' ')
    day = int(day_str)
    month = month_str_to_month(month_str)
    year = int(year_str)
    time = datetime.time.fromisoformat(time_str)
    return datetime.datetime(
        year, month, day,
        time.hour, time.minute, time.second,
        tzinfo=datetime.timezone.utc)


def line_to_manifest(line):
    datetime_part, utc, rest = line.partition('UTC')
    datetime = parse_datetime(datetime_part + ' ' + utc)
    _, _, manifest_code = rest.rpartition(' ')
    return Manifest(int(manifest_code), datetime)


def load_file(file_name):
    manifest_list_content = open(file_name).read()
    manifest_all_lines = manifest_list_content.split('\n')
    manifest_lines = [m for m in manifest_all_lines if m and '#' not in m]
    manifests = [line_to_manifest(line) for line in manifest_lines]
    return manifests
