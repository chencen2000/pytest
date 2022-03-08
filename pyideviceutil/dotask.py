import os
import sys
import json
import click
import uuid
import logging
import plistlib
import tempfile


from pymobiledevice3 import usbmux
from pymobiledevice3.lockdown import LockdownClient
from pymobiledevice3.services.mobile_config import MobileConfigService
from pymobiledevice3.services.installation_proxy import InstallationProxyService

logging.basicConfig(format='%(asctime)s #%(lineno)d: [%(funcName)s] %(message)s', level=logging.INFO)

def genWiFi_mobileconfig(wifi):
    logging.info(f'input wifi={wifi}')
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
    fp = tempfile.TemporaryFile()
    plistlib.dump(pl, fp)
    fp.seek(0)
    logging.info(f'generated dict: {pl}')
    return fp

def getLockdownClient(udid):
    ret = None
    logging.info(f'udid={udid}')
    try:
        devs = usbmux.list_devices()
        for d in devs:
            if udid==d.serial:
                ret = LockdownClient(udid)
                break
        else:
            logging.error(f'Device({udid}) not found.')
    except:
        logging.exception('exception on list devices')
    logging.info(f'ret={ret}')
    return ret

@click.group()
def cli():
    pass

@cli.command()
@click.option('--udid', type=str)
@click.argument('filename')
def config(filename, udid):
    """config by json file"""
    # print(f'config {filename} on device {udid}.')
    logging.info(f'configfile={filename}, device={udid}.')
    lockdown = getLockdownClient(udid)
    if lockdown is None:
        logging.error(f'device {udid} not ready.')
    else:
        with open(filename, 'rb') as fp:
            config_data = json.load(fp)
        if 'wifi' in config_data:
            try:
                fp = genWiFi_mobileconfig(config_data['wifi'])
                # lockdown = LockdownClient(udid)
                service = MobileConfigService(lockdown=lockdown)
                service.install_profile(fp.read())
                fp.close()
                print('Success install Wi-Fi Profile')
            except:
                logging.exception('exception in install Wi-Fi Profile.')
        if 'app' in config_data:
            for f in config_data['app']:
                if os.path.exists(f):
                    try:
                        InstallationProxyService(lockdown=lockdown).install_from_local(f)
                        print(f'Success install app {f}')
                    except:
                        logging.exception(f'exception in install app {f}')            


if __name__ == '__main__':
    cli()