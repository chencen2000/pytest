import os
import sys
import uuid
import json
import click
import logging
import plistlib
import subprocess
import commands.env as env
import commands.listdevices as listdevices

def genWiFi_mobileconfig(wifi, root):
    # logging.info(f'input wifi={wifi}')
    guid = str(uuid.uuid4()).upper()
    pl = dict(
        PayloadContent=[],
        PayloadDisplayName='Wi-Fi Profile',
        PayloadIdentifier=f'futuredials-mac-mini.local.{guid}',
        PayloadRemovalDisallowed=False,
        PayloadType='Configuration',
        PayloadUUID=guid,
        PayloadVersion=1
    )
    for w in wifi:
        guid = str(uuid.uuid4()).upper()
        p = dict(
            AutoJoin=True,
            EncryptionType='Any',
            HIDDEN_NETWORK=False,
            IsHotspot=False,
            PayloadType='com.apple.wifi.managed',
            PayloadUUID=guid,
            PayloadDisplayName='Wi-Fi',
            PayloadDescription='Wi-Fi settings',
            PayloadIdentifier=f'futuredials-mac-mini.local.{guid}',
            PayloadVersion=1,
            SSID_STR=w['ssid'],
            Password=w['password']
        )
        pl['PayloadContent'].append(p)
    fn = os.path.join(root, 'wifi.mobileconfig')
    with open(fn, 'wb') as fp:
        plistlib.dump(pl, fp)
    # logging.info(f'generated dict: {pl}')
    return fn

def validate_device(udid, root):
    tool = os.path.join(root, 'bin', 'idevicepair')
    if os.path.exists(tool):
        my_env = os.environ.copy()
        my_env['LD_LIBRARY_PATH'] = os.path.join(root, 'lib')
        p = subprocess.Popen([tool, '--udid', udid, 'validate'], env=my_env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output = p.communicate()
        code = p.returncode
        return code

def install_mobileconfig(udid, fn, root):
    tool = os.path.join(root, 'bin', 'ideviceprofile')
    if os.path.exists(tool):
        my_env = os.environ.copy()
        my_env['LD_LIBRARY_PATH'] = os.path.join(root, 'lib')
        p = subprocess.Popen([tool, '--udid', udid, 'install', fn], env=my_env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output = p.communicate()
        code = p.returncode
        print(output[0].decode('utf-8'))

def install_app(udid, fn, root):
    tool = os.path.join(root, 'bin', 'ideviceinstaller')
    if os.path.exists(tool):
        my_env = os.environ.copy()
        my_env['LD_LIBRARY_PATH'] = os.path.join(root, 'lib')
        p = subprocess.Popen([tool, '--udid', udid, '-i', fn], env=my_env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output = p.communicate()
        code = p.returncode
        print(output[0].decode('utf-8'))

@click.command()
@click.option('--udid', type=str)
@click.argument('filename')
def dotask(filename, udid):
    """config Apple devices by udid"""
    # click.echo(f'dotask: {filename} on {udid}')
    ret = 1
    root = env.env_prepare()
    devs = listdevices.get_devices(root.name)
    if udid in devs:
        if validate_device(udid, root.name) == 0:
            with open(filename) as fp:
                data = json.load(fp)
            if 'wifi' in data:
                fn = genWiFi_mobileconfig(data['wifi'], root.name)
                install_mobileconfig(udid, fn, root.name)
            if 'app' in data:
                for fn in data['app']:
                    if os.path.exists(fn):
                        install_app(udid, fn, root.name)
                    else:
                        click.echo(f'{fn} not exits.')
            ret = 0
        else:
            ret = 3
    else:
        ret = 2
    root.cleanup()
    sys.exit(ret)

if __name__ == '__main__':
    dotask()
