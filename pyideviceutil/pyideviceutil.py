import click
from test_cli import cli as test_cli1
from listdevice import cli as listdevice_cli
from dotask import cli as dotask_cli

cli = click.CommandCollection(sources=[listdevice_cli, dotask_cli, test_cli1])

if __name__ == '__main__':
    cli()