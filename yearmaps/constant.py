import hashlib
from dataclasses import dataclass
from datetime import timedelta
from copy import deepcopy


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
        a = deepcopy(self)
        a.output = None
        return hashlib.md5(str(a).encode('UTF-8')).hexdigest()


ONE_DAY = timedelta(days=1)
