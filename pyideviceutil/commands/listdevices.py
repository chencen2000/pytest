import os
import sys
import click
import subprocess
import commands.env as env

def get_devices(root):
    devs = []
    x = os.path.join(root, 'bin', 'idevice_id')
    if os.path.exists(x):
        my_env = os.environ.copy()
        my_env['LD_LIBRARY_PATH'] = os.path.join(root, 'lib')
        p = subprocess.Popen([x, '-l'], env=my_env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output = p.communicate()
        if len(output[0]) > 0:
            # lines = output[0].decode('utf-8').split('\n')
            devs = output[0].decode('utf-8').splitlines()
    return [x for x in devs if bool(x)]

@click.command()
def list_device():
    """list Apple devices"""
    ret = 1
    root = env.env_prepare()
    devs = get_devices(root.name)
    if len(devs)>0:
        for d in devs:
            print(d)
        ret = 0
    else:
        print('No iDevices found.')
        ret = 1
    # f = os.path.join(root.name, 'bin', 'idevice_id')
    # if os.path.exists(f):
    #     my_env = os.environ.copy()
    #     my_env['LD_LIBRARY_PATH'] = os.path.join(root.name, 'lib')
    #     p = subprocess.Popen([f, '-l'], env=my_env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    #     output = p.communicate()
    #     if len(output[0]) > 0:
    #         print(output[0].decode('utf-8'))
    root.cleanup()
    sys.exit(ret)

if __name__ == '__main__':
    list_device()
