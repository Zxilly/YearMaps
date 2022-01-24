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
    if obj.get(Config.SERVER, False):
        return f"{provider_id}.{obj[Config.COLOR]}.{obj[Config.MODE]}.{obj[Config.YEAR]}.{obj[Config.FILE_TYPE]}"
    return f"{provider_id}.{obj[Config.FILE_TYPE]}"
