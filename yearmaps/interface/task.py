import hashlib
from copy import deepcopy
from pathlib import Path
from typing import Dict
from datetime import date

import click

from yearmaps.constant import Config, Configs


class Task:
    def __init__(self,
                 context: click.Context,
                 command: click.Command,
                 global_options: Dict,
                 options: Dict):
        self.command = command
        self.options = options
        self.context = deepcopy(context)
        self.obj: Configs = self.context.obj
        for key, value in global_options:
            setattr(self.obj, key, value)

    def run(self, force=False):
        if self.should_run() or force:
            self.context.invoke(self.command, **self.options)

    def should_run(self) -> bool:
        if self.context.obj.mode == 'year':
            if date.today().year == self.obj.year:
                return True
        return False

    def task_name(self) -> str:


    def cache_path(self) -> Path:
        return Path(self.obj.output_dir) / self.cache_name()

    def ensure_cache(self, quiet=False):
        if not quiet:
            click.echo(f"Ensuring cache for {self.cache_name()}")
        if not self.cache_path().exists():
            self.run(force=True)
