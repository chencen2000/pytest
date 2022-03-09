import click
import struct

# from test_cli import config
from commands.listdevices import list_device
from commands.dotask import dotask

@click.group()
def cli():
    pass

@cli.command()
def version():
    """Show version"""
    click.echo(f'Version 1.0 ({8*struct.calcsize("P")}-bit)')

if __name__ == '__main__':
    cli.add_command(dotask, 'config')
    cli.add_command(list_device, "list")
    cli()