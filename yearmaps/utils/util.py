from datetime import timedelta, date
import os


def date_range(start_date: date, end_date: date):
    for n in range(int((end_date - start_date).days) + 1):
        yield start_date + timedelta(n)


def is_debug():
    return os.environ.get('DEBUG', 'False') != 'False'
