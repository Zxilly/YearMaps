import hashlib
from copy import deepcopy
from pathlib import Path
from typing import Dict
from datetime import date

import click

from yearmaps.constant import Config
from yearmaps.utils.util import get_file_prefix, get_file_identifier


class Task:
    def __init__(self,
                 context: click.Context,
                 command: click.Command,
                 global_options: Dict,
                 options: Dict):
        self.command = command
        self.options = options
        self.context = deepcopy(context)
        obj = self.context.obj
        obj.update(global_options)

    def run(self, force=False):
        if self.should_run() or force:
            self.context.invoke(self.command, **self.options)

    def should_run(self) -> bool:
        if self.context.obj[Config.MODE] == 'year':
            if date.today().year == self.context.obj[Config.YEAR]:
                return True
        return False

    def cache_file_prefix(self) -> str:
        return get_file_identifier(self.command.name, self.context.obj)

    def cache_file_name_hash(self) -> str:
        file_prefix = get_file_identifier(self.command.name, self.context.obj)
        return hashlib.md5(file_prefix.encode('utf-8')).hexdigest()

    def server_name(self) -> str:
        file_hash = self.cache_file_name_hash()
        return f"{file_hash}.{self.context.obj[Config.FILE_TYPE]}"

    def cache_name(self) -> str:
        file_prefix = self.cache_file_prefix()
        return f"{file_prefix}.{self.context.obj[Config.FILE_TYPE]}"

    def cache_path(self) -> Path:
        return Path(self.context.obj[Config.OUTPUT_DIR]) / self.cache_name()

    def ensure_cache(self, quiet=False):
        if not quiet:
            click.echo(f"Ensuring cache for {self.cache_name()}")
        if not self.cache_path().exists():
            self.run(force=True)
