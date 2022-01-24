from datetime import timedelta, date
import os
from typing import Dict

from yearmaps.constant import Config


def date_range(start_date: date, end_date: date):
    for n in range(int((end_date - start_date).days) + 1):
        yield start_date + timedelta(n)


def is_debug():
    return os.environ.get('DEBUG', 'False') != 'False'


def get_filename(provider_id: str, obj: Dict):
    return get_file_prefix(provider_id, obj) + '.' + obj[Config.FILE_TYPE]


def get_file_prefix(provider_id: str, obj: Dict):
    if obj.get(Config.SERVER, False):
        return f"{get_file_identifier(provider_id, obj)}.{date_encode()}"
    return f"{provider_id}"


def get_file_identifier(provider_id: str, obj: Dict):
    return f"{provider_id}.{obj[Config.COLOR]}.{obj[Config.MODE]}.{obj[Config.YEAR]}"


def date_encode():
    return date.today().strftime("%Y%m%d")


def date_decode(date_str: str):
    return date(int(date_str[:4]), int(date_str[4:6]), int(date_str[6:]))
