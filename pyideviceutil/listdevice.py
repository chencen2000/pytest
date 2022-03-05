import click
from pymobiledevice3 import usbmux

@click.group()
def cli():
    pass

@cli.command()
def list_devices():
    """list Apple devices"""
    devs = usbmux.list_devices()
    for d in devs:
        print(d.serial)

if __name__ == '__main__':
    cli()