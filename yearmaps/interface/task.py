from copy import deepcopy
from typing import Dict

import click


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
        obj.update(global_options) # FIXME: add default global options

    def run(self):
        self.context.invoke(self.command, **self.options)
