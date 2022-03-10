import os
import struct
import tarfile
import tempfile

def env_prepare(folder=None):
    folder_name = ''
    if folder is not None and os.path.exists(folder):
        folder_name = folder
    else:
        folder = tempfile.TemporaryDirectory()
        folder_name = folder.name
    # i = 8*struct.calcsize("P")
    # tar_filename = r'/home/qa/Downloads/tools.tar.gz'    
    tar_filename = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))),f'tools.tar.gz')
    # if i == 64:
    #     tar_filename = f'tools_x{i}.tar.gz'
    # elif i == 32:
    #     tar_filename = r'/home/qa/Downloads/tools.tar.gz'
    try:
        if os.path.exists(tar_filename):
            tar = tarfile.open(tar_filename)
            tar.extractall(folder_name)
            tar.close()
        else:
            print(f'{tar_filename} not exits.')
    except:
        pass
    return folder

def env_cleanup():
    pass

if __name__ == '__main__':
    f = env_prepare()
    f.cleanup()