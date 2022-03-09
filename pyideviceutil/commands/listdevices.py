import os
import click
import subprocess
import commands.env as env

@click.command()
def list_device():
    """list Apple devices"""
    root = env.env_prepare()
    f = os.path.join(root.name, 'bin', 'idevice_id')
    if os.path.exists(f):
        my_env = os.environ.copy()
        my_env['LD_LIBRARY_PATH'] = os.path.join(root.name, 'lib')
        p = subprocess.Popen([f, '-l'], env=my_env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output = p.communicate()
        if len(output[0]) > 0:
            print(output[0].decode('utf-8'))
    root.cleanup()
    pass

if __name__ == '__main__':
    list_device()
