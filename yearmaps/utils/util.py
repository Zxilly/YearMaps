import hashlib
from datetime import date


def date_encode():
    return date.today().strftime("%Y%m%d")


def date_decode(date_str: str):
    return date(int(date_str[:4]), int(date_str[4:6]), int(date_str[6:]))


def dict_hash(d: dict) -> str:
    return hashlib.md5(str(frozenset(d.items())).encode('UTF-8')).hexdigest()


def str_hash(*s: str) -> str:
    return hashlib.md5(("".join(s)).encode('UTF-8')).hexdigest()
