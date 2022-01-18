import os
from datetime import datetime

import click

from yearmaps.constant import config
from yearmaps.providers import providers
from yearmaps.utils import default_data_dir


@click.group()
@click.option('--data-dir', '-d', default=str(default_data_dir()), type=str, show_default=True,
              help='Directory to store data')
@click.option('--output-dir', '-o', default=os.getcwd(), type=str, show_default=True,
              help='Directory to store output')
@click.option('--mode', '-m', default='till_now', type=click.Choice(['till_now', 'year']), show_default=True,
              help='Generate mode of the program')
@click.option('--year', '-y', default=datetime.now().year, type=int, show_default=True,
              help='Year to generate, this options depends on mode=year')
@click.pass_context
def cli(ctx: click.Context, data_dir: str, output_dir: str, mode: str, year: int):
    ctx.ensure_object(dict)
    obj = ctx.obj
    obj[config.DATA_DIR] = data_dir
    obj[config.OUTPUT_DIR] = output_dir
    if mode == 'year':
        obj[config.MODE] = mode
        obj[config.YEAR] = year
    else:
        obj[config.MODE] = mode


def main():
    for provider in providers:
        cli.add_command(provider.command)
    cli()


if __name__ == '__main__':
    main()
