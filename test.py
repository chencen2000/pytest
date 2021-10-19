import os
import re
import time
import threading
import subprocess

def listiPhone(apsthome):
    ret = []
    wd = os.path.join(apsthome, 'tools', 'winiMobileDevice')
    fn = os.path.join(wd, 'idevice_id.exe')
    if os.path.exists(wd) and os.path.exists(fn):
        p = subprocess.Popen([fn], stdout=subprocess.PIPE, cwd=wd)
        p.wait()
        s = p.communicate()
        lines = s[0].decode().split('\r\n')
        for s in lines:            
            x = re.search('([0-9a-fA-F\-]+) \((\w+)\)', s)
            if x is not None:
                ret.append(x.groups()[0])
    return ret

def wait_for_device(udid, apsthome, timeout=100):
    print(f'wait_for_device: ++ udid={udid}')
    found = False
    t0 = time.time()
    while not found:
        if time.time() - t0 > timeout:
            print(f'wait_for_device: Error, after {timeout} seconds, still seen device udid={udid}')
            break
        time.sleep(3)
        devices = listiPhone(apsthome)    
        for d in devices:
            if d == udid:
                found = True
    print(f'wait_for_device: -- udid={udid} ret={found}')
    return found

def restart_per_device_1(udid, apsthome, wait=0):
    print(f'restart_per_device_1: ++ udid={udid}')
    wd = os.path.join(apsthome, 'phonedll', 'PST_APE_UNIVERSAL_USB_FD', 'resource')
    fn = os.path.join(wd, 'iDeviceUtilCore.exe')
    cmd = [fn, '--udid', udid, '--restart', '1']
    p = subprocess.Popen(cmd, cwd=wd)
    p.wait()
    ret = p.returncode
    print(f'restart_per_device_1: [{udid}]: {fn} return={ret}')
    if wait > 0:
        time.sleep(10)
        ret = wait_for_device(udid, apsthome, wait)
    print(f'restart_per_device_1: -- [{udid}]: return={ret}')

def restart_per_device_2(udid, apsthome, wait=0):
    print(f'restart_per_device_2: ++ udid={udid}')
    info = get_device_info(apsthome, udid)
    wd = os.path.join(apsthome, 'tools', 'winiMobileDevice')
    fn = os.path.join(wd, 'idevicediagnostics.exe')
    cmd = [fn, '--udid', udid, 'restart']
    p = subprocess.Popen(cmd, cwd=wd)
    p.wait()
    ret = p.returncode
    print(f'restart_per_device_2: [{udid}]: {fn} return={ret}')
    if wait > 0:
        time.sleep(30)
        ret = wait_for_device(udid, apsthome, wait)
    print(f'restart_per_device_2: -- [{udid}]: return={ret}')

def restart_per_device_3(udid, apsthome, wait=0):
    print(f'restart_per_device_3: ++ udid={udid}')
    wd = os.path.join(apsthome, 'phonedll', 'PST_APE_UNIVERSAL_USB_FD', 'resource')
    fn = os.path.join(wd, 'iDeviceUtilCore.exe')
    cmd = [fn, '--udid', udid, '--restart', '1']
    p = subprocess.Popen(cmd, cwd=wd)
    p.wait()
    ret = p.returncode
    print(f'restart_per_device_3: [{udid}]: {fn} return={ret}')
    if wait > 0:
        time.sleep(10)
        ret = wait_for_device(udid, apsthome, wait)
    print(f'restart_per_device_3: -- [{udid}]: return={ret}')

def restart_device(devices, apsthome):
    print('restart_device: ++')
    tasks = []
    for dev in devices:
        # restart_per_device(dev, apsthome)
        t = threading.Thread(target=restart_per_device_1, args=(dev, apsthome,), daemon=True)
        # t = threading.Thread(target=restart_per_device_2, args=(dev, apsthome,), daemon=True)
        t.start()
        tasks.append(t)
    print('restart_device: wait for all tasks complete.')
    for t in tasks:
        t.join()
    print('restart_device: --')

def get_device_info(apsthome, udid):
    info = {}
    wd = os.path.join(apsthome, 'phonedll', 'PST_APE_UNIVERSAL_USB_FD', 'resource')
    fn = os.path.join(wd, 'iDeviceUtilCore.exe')
    cmd = [fn, '--udid', udid, '--info']
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, cwd=wd)
    p.wait()
    s = p.communicate()
    lines = s[0].decode().split('\r\n')
    for l in lines:
        pos = l.find('=')
        if pos>0:
            k = l[:pos]
            v = l[pos+1:]
            info[k] = v
    return info


apsthome = os.getenv('apsthome', r'C:\\ProgramData\\Futuredial\\CMC')
devs = listiPhone(apsthome)
print(f'There are {len(devs)} devices found.')
print(devs)
# restart_device([devs[0]], apsthome)
restart_device(devs, apsthome)
# info = get_device_info(apsthome, devs[0])
# print(info)
