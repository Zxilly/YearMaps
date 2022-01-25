import os

import click

from yearmaps.constant import Config
from yearmaps.provider import providers
from yearmaps.utils.colors import color_list
from yearmaps.utils.file import default_data_dir


@click.group()
@click.option('--data-dir', '-d', default=str(default_data_dir()), type=str, show_default=True,
              help='Directory to store datas')
@click.option('--output-dir', '-o', default=os.getcwd(), type=str, show_default=True,
              help='Directory to store output')
@click.option('--file-type', '-f', default='svg', type=click.Choice(['svg', 'png']), show_default=True,
              help='File type to export')
@click.option('--mode', '-m', default='till_now', type=click.Choice(['till_now', 'year']), show_default=True,
              help='Generate mode of the program')
@click.option('--year', '-y', type=int,
              help='Year to generate, this option will override mode to "year"')
@click.option('--color', '-c', type=click.Choice(color_list.keys()),
              help='Color to override provider default color')
@click.pass_context
def cli(ctx: click.Context, data_dir: str, output_dir: str, file_type: str, mode: str, year: int, color: str):
    ctx.ensure_object(dict)
    obj = ctx.obj
    obj[Config.DATA_DIR] = data_dir
    obj[Config.OUTPUT_DIR] = output_dir
    obj[Config.FILE_TYPE] = file_type
    obj[Config.COLOR] = color
    if year is not None:
        if mode == 'till_now':
            mode = 'year'
    if mode == 'year':
        obj[Config.MODE] = mode
        obj[Config.YEAR] = year
    else:
        obj[Config.MODE] = mode


def main():
    for provider in providers:
        cli.add_command(provider.command)
    cli()


if __name__ == '__main__':
    main()
