import os
import click
import struct
import shutil

# from test_cli import config
from commands.listdevices import list_device
from commands.dotask import dotask
from commands.env import env_prepare

@click.group()
def cli():
    pass

@cli.command()
def version():
    """Show version"""
    click.echo(f'Version 22.3.9.1 ({8*struct.calcsize("P")}-bit)')

@cli.command()
@click.argument('folder')
def extract(folder):
    """Extract Toolset to folder"""
    # click.echo(__file__)
    # click.echo(os.path.realpath(__file__))
    # f = os.path.dirname(os.path.realpath(__file__))
    # click.echo(f'cwd: {f}')
    # click.echo(f'{os.listdir(f)}')
    # click.pause()
    root = env_prepare(folder)
    # shutil.move(os.path.join(root.name,'*'), folder)
    # shutil.copytree(root.name, folder)
    # root.cleanup()
    # click.pause()

if __name__ == '__main__':
    cli.add_command(dotask, 'config')
    cli.add_command(list_device, "list")
    cli()