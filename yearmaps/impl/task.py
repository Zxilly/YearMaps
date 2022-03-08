from copy import deepcopy
from datetime import date
from pathlib import Path
from typing import Dict

import click

from yearmaps.constant import Configs
from yearmaps.utils.util import dict_hash, str_hash


class Task:
    def __init__(self,
                 name: str,
                 context: click.Context,
                 command: click.Command,
                 global_options: Dict,
                 options: Dict):
        self.name = name
        self.command = command
        self.command_options = options
        self.context = deepcopy(context)
        self.global_config: Configs = self.context.obj
        for key, value in global_options.items():
            setattr(self.global_config, key, value)
        self.global_config.output = str(Path(
            self.global_config.output) / f"{self.task_hash()}.{self.global_config.file_type}")

    def run(self, force=False):
        if self.should_run() or force:
            self.context.invoke(self.command, **self.command_options)

    def should_run(self) -> bool:
        if self.context.obj.mode == 'year':
            return date.today().year == self.global_config.year
        return True

    def task_hash(self) -> str:
        command_options_hash = dict_hash(self.command_options)
        global_options_hash = self.global_config.hash()
        return str_hash(command_options_hash, global_options_hash, self.command.name)

    def cache_path(self) -> Path:
        return Path(self.global_config.output)

    def task_name(self) -> str:
        return f"{self.command.name} {self.command_options} {self.global_config} \n{self.task_hash()}"

    def update_cache(self):
        click.echo(f"Updating cache for {self.global_config} {self.command_options}")
        self.run(force=True)

    def ensure_cache(self, quiet=False):
        if not quiet:
            click.echo(f"Ensuring cache for {self.global_config} {self.command_options}")
        self.run(force=True)
