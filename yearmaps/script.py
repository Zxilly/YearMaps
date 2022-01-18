import click
from providers import providers
from utils import default_data_dir


@click.group
@click.option('--data-dir', default=default_data_dir(), show_default=True, help='Directory to store data')
@click.pass_context
def cli(ctx: click.Context, data_dir: str):
    ctx.ensure_object(dict)
    obj = ctx.obj
    obj['DATA-DIR'] = data_dir


def main():
    for provider in providers:
        cli.add_command(provider.command)
    cli()


if __name__ == '__main__':
    main()
