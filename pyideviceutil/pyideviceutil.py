from plistlib import FMT_XML
import sys
import click
# from test_cli import cli as test_cli1
from listdevice import cli as listdevice_cli
from dotask import cli as dotask_cli

def run_pymobiledevice3():
    import runpy
    del sys.argv[1]
    runpy.run_module("pymobiledevice3", run_name='__main__')

def test():
    import plistlib
    with open('iOSautoOpenWifi.mobileconfig', 'rb') as fp:
        data = plistlib.load(fp)
    print(data)


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv)>1 else ''
    if cmd == 'pymd':
        run_pymobiledevice3()
    elif cmd == 'test':
        test()
    else:
        cli = click.CommandCollection(sources=[listdevice_cli, dotask_cli])
        cli()