import hashlib
import json
from pathlib import Path
from datetime import datetime


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


def update_time(cache_dir: str):
    path = Path(cache_dir) / ".update_time"
    with open(path, 'w', encoding="UTF-8") as f:
        f.write(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))


def get_update_time(cache_dir: str) -> str:
    path = Path(cache_dir) / ".update_time"
    if not path.exists():
        return "Never updated."
    with open(path, 'r', encoding="UTF-8") as f:
        return str(f.read())
