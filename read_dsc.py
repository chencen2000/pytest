import os
from io import SEEK_SET
from struct import *
from uuid import UUID
from UnifiedLog import data_format

def dsc_version_1(fd, num_range_entries, num_uuid_entries):
    binData = data_format.BinaryDataFormat()
    fd.seek(16, SEEK_SET)
    range_entries = []
    uuid_entries= []
    while len(range_entries) < num_range_entries:
        buf = fd.read(16)
        idx, v_off, data_off, size = unpack('<IIII', buf)
        range_entries.append([idx,v_off,data_off,size])
        pass
    pos = fd.tell()
    while len(uuid_entries) < num_uuid_entries:
        fd.seek(pos, SEEK_SET)
        buf = fd.read(28)
        pos = fd.tell()
        v_off, size = unpack("<II", buf[:8])
        uuid_object = UUID(bytes=buf[8:24])
        pos1 = unpack("<I", buf[24:])[0]
        fd.seek(pos1, SEEK_SET)
        buf = fd.read(1024) # File path should not be >1024
        lib_path = binData._ReadCString(buf)
        lib_name = os.path.basename(lib_path)
        uuid_entries.append([v_off, size, uuid_object, lib_path, lib_name])
        pass
    return range_entries, uuid_entries

def dsc_version_2(fd, num_range_entries, num_uuid_entries):
    binData = data_format.BinaryDataFormat()
    fd.seek(16, SEEK_SET)
    range_entries = []
    uuid_entries= []
    while len(range_entries) < num_range_entries:
        buf = fd.read(24)
        v_off, data_off, size, idx = unpack('<QIIQ', buf)
        range_entries.append([idx,v_off,data_off,size])
        pass
    pos = fd.tell()
    while len(uuid_entries) < num_uuid_entries:
        fd.seek(pos, SEEK_SET)
        buf = fd.read(32)
        pos = fd.tell()
        v_off, size = unpack("<QI", buf[:12])
        uuid_object = UUID(bytes=buf[12:28])
        pos1 = unpack("<I", buf[28:])[0]
        fd.seek(pos1, SEEK_SET)
        buf = fd.read(1024) # File path should not be >1024
        lib_path = binData._ReadCString(buf)
        lib_name = os.path.basename(lib_path)
        uuid_entries.append([v_off, size, uuid_object, lib_path, lib_name])
        pass
    return range_entries, uuid_entries

def read_dsc(fn):
    range_entries = []
    uuid_entries = []
    fd = open(fn, 'rb')
    buf = fd.read(16)
    if buf[0:4] == b'hcsd':
        major_version, minor_version, num_range_entries, num_uuid_entries = (unpack("<HHII", buf[4:16]))
        print(f'version: {major_version}.{minor_version}')
        print(f'num_range_entries: {num_range_entries}')
        print(f'num_uuid_entries: {num_uuid_entries}')
        if major_version ==1:        
            range_entries, uuid_entries = dsc_version_1(fd, num_range_entries, num_uuid_entries)
        elif major_version ==2:
            range_entries, uuid_entries = dsc_version_2(fd, num_range_entries, num_uuid_entries)
        else:
            print(f'version: {major_version}.{minor_version}. not Support.')
    fd.close()
    return range_entries, uuid_entries

# fn = "E:\\logs\\iPhone\\iOS14\\1.logarchive\\dsc\\549CED3ECA16D9A4FDFF6880F584B371"
fn = "E:\\logs\\iPhone\\1c54319dc1bdb017141bfcf70445764666595478\\log.logarchive\\dsc\\5E5347048EEB327B9D0D4F8C3777B9A5"
r, u = read_dsc(fn)
for x in r:
    print(x)
for x in u:
    print(x)

