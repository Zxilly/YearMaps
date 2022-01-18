import click
from providers import providers


@click.Group
def group():
    pass


def main():
    for provider in providers:
        group.add_command(provider.command)
    group()


if __name__ == '__main__':
    main()
