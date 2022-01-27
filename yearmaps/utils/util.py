import hashlib
import json


def dict_hash(d: dict) -> str:
    return hashlib.md5(json.dumps(d, sort_keys=True).encode('UTF-8')).hexdigest()


def str_hash(*s: str) -> str:
    return hashlib.md5(("".join(s)).encode('UTF-8')).hexdigest()
