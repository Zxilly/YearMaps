from datetime import timedelta, date
import os
from typing import Dict

from yearmaps.constant import Config


def date_range(start_date: date, end_date: date):
    for n in range(int((end_date - start_date).days) + 1):
        yield start_date + timedelta(n)


def is_debug():
    return os.environ.get('DEBUG', 'False') != 'False'


def get_filename(provider: str, obj: Dict):
    if str(Config.SERVER) in obj:
        return f"{provider}.{obj[Config.COLOR]}.{obj[Config.MODE]}.{obj[Config.YEAR]}.{obj[Config.FILE_TYPE]}"
    return f"{provider}.{obj[Config.FILE_TYPE]}"
