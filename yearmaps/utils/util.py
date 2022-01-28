import hashlib
import json


def dict_hash(d: dict) -> str:
    return hashlib.md5(json.dumps(d, sort_keys=True).encode('UTF-8')).hexdigest()


def str_hash(*s: str) -> str:
    return hashlib.md5(("".join(s)).encode('UTF-8')).hexdigest()


def option_name(name: str) -> str:
    if name.startswith('--'):
        name = name[2:]
    elif name.startswith('-'):
        name = name[1:]
    name = name.replace('-', '_')
    name = name.lower()
    return name
