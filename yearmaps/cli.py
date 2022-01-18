import click
from providers import providers


@click.Group
@click.option('--data-dir',default='data',help='Directory to store data')
@click.pass_context
def group(ctx: click.Context):
    ctx.ensure_object(dict)


def main():
    for provider in providers:
        group.add_command(provider.command)
    group()


if __name__ == '__main__':
    main()
