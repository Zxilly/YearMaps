import hashlib
from dataclasses import dataclass
from datetime import timedelta


@dataclass
class Configs:
    data_dir: str
    output: str
    mode: str
    file_type: str
    year: int = None
    color: str = None
    server: bool = None

    def hash(self):
        return hashlib.md5(str(self).encode()).hexdigest()


ONE_DAY = timedelta(days=1)
