import os
import struct
import tarfile
import tempfile

def env_prepare():
    folder = tempfile.TemporaryDirectory()
    i = 8*struct.calcsize("P")
    tar_filename = r'/home/qa/Downloads/tools.tar.gz'
    tar_filename = f'tools_x{i}.tar.gz'
    # if i == 64:
    #     tar_filename = f'tools_x{i}.tar.gz'
    # elif i == 32:
    #     tar_filename = r'/home/qa/Downloads/tools.tar.gz'
    if os.path.exists(tar_filename):
        tar = tarfile.open(tar_filename)
        tar.extractall(folder.name)
        tar.close()
    return folder

def env_cleanup():
    pass

if __name__ == '__main__':
    f = env_prepare()
    f.cleanup()