import click
import logging
from pymobiledevice3 import usbmux

logging.basicConfig(format='%(asctime)s #%(lineno)d: [%(funcName)s] %(message)s', level=logging.INFO)

@click.group()
def cli():
    pass

@cli.command()
def list_devices():
    """list Apple devices"""
    try:
        devs = usbmux.list_devices()
        for d in devs:
            print(d.serial)
    except:
        logging.exception('exception on list_devices')

if __name__ == '__main__':
    cli()