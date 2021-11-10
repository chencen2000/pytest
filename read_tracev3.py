import os
import struct
import binascii
import lz4.block
from UnifiedLog import data_format


def parse_header_chunk(tag, subtag, chunk_data):
    chunk_len = len(chunk_data)
    pass

def parse_catalog_chunk(tag, subtag, chunk_data):
    binData = data_format.BinaryDataFormat()
    chunk_len = len(chunk_data)
    # with open('E:\\logs\\iPhone\\output\\catalog.bin', 'wb') as f:
    #     f.write(chunk_data)
    pos = 0
    (subsystem_strings_offset, proc_infos_offset, number_of_proc_infos,sub_chunk_offset, num_sub_chunks_to_follow) = (struct.unpack('<HHHHH', chunk_data[pos:pos+10]))
    pos += 16
    (cont_time) = (struct.unpack('<Q', chunk_data[pos:pos+8]))
    pos += 8
    subsystem_strings_offset += pos
    proc_infos_offset += pos
    sub_chunk_offset += pos
    while pos < subsystem_strings_offset:
        file_path_data = chunk_data[pos:pos+16]
        file_path = binascii.hexlify(file_path_data).decode('utf8')
        file_path = file_path.upper()
        print(file_path)
        pos += 16
    subsystem_strings = chunk_data[pos:proc_infos_offset]
    pos = proc_infos_offset
    while pos < sub_chunk_offset:
        (id, flags, file_id, dsc_file_index, proc_id1, proc_id2, pid, euid,
             u6, num_extra_uuid_refs, u8) = struct.unpack('<HHhhQIIIIII', chunk_data[pos:pos+40])
        pos += 40
        uuid_infos_end_offset = pos + (16 * num_extra_uuid_refs)
        while pos < uuid_infos_end_offset:
            (size, u10, uid) = struct.unpack('<IIH', chunk_data[pos:pos+10])
            pos +=10
            address = int.from_bytes(chunk_data[pos:pos+6], 'little')
            pos += 6
        (num_subsys_cat_elements, u9) = struct.unpack('<II', chunk_data[pos:pos+8])
        pos += 8
        sub_systems_end_offset = pos + (6 * num_subsys_cat_elements)
        while pos < sub_systems_end_offset:
            item_id, subsystem_offset, category_offset = struct.unpack('<HHH', chunk_data[pos:pos+6])
            pos += 6
            subsystem_string = binData._ReadCString(subsystem_strings[subsystem_offset:])
            category_string = binData._ReadCString(subsystem_strings[category_offset:])
            print(f'{item_id}, {subsystem_offset}({subsystem_string}), {category_offset}({category_string})')
        _, remainder = divmod(pos, 8)
        if remainder > 0:
            i = 8 - remainder    
            pos += i
    while pos < chunk_len:
        pass

def _DecompressChunkData(chunk_data, data_len):
    '''Decompress an individual compressed chunk (tag=0x600D)'''
    uncompressed = b''
    if chunk_data[0:4] in [b'bv41', b'bv4-']:
        last_uncompressed = b''
        comp_start = 0 # bv** offset
        comp_header = chunk_data[comp_start:comp_start + 4]
        while (data_len > comp_start) and (comp_header != b'bv4$'):
            if comp_header == b'bv41':
                uncompressed_size, compressed_size = struct.unpack('<II', chunk_data[comp_start + 4:comp_start + 12])
                last_uncompressed = lz4.block.decompress(chunk_data[comp_start + 12: comp_start + 12 + compressed_size], uncompressed_size, dict=last_uncompressed)
                comp_start += 12 + compressed_size
                uncompressed += last_uncompressed
            elif comp_header == b'bv4-':
                uncompressed_size = struct.unpack('<I', chunk_data[comp_start + 4:comp_start + 8])[0]
                uncompressed += chunk_data[comp_start + 8:comp_start + 8 + uncompressed_size]
                comp_start += 8 + uncompressed_size
            else:
                print('Unknown compression value {} @ 0x{:X} - {}'.format(binascii.hexlify(comp_header), comp_start, comp_header))
                break
            comp_header = chunk_data[comp_start:comp_start + 4]
    else:
        print('Unknown compression type {}'.format(binascii.hexlify(chunk_data[16:20])))
    return uncompressed

def parse_6001_chunk(tag, subtag, chunk_data):
    chunk_len = len(chunk_data)
    with open('E:\\logs\\iPhone\\output\\chunk_6001.bin', 'wb') as f:
        f.write(chunk_data)
    pos = 0
    pid1 = int.from_bytes(chunk_data[pos:pos+8])
    pos += 8
    pid2 = int.from_bytes(chunk_data[pos:pos+4])
    pos += 4
    collapsed = int.from_bytes(chunk_data[pos:pos+1])
    pos += 4
    public_data_size = int.from_bytes(chunk_data[pos:pos+2])
    pos += 2
    private_data_size = int.from_bytes(chunk_data[pos:pos+2])
    pos += 2
    pos += 2
    pos += 2
    base_time = int.from_bytes(chunk_data[pos:pos+8])

def parse_600D_chunk(tag, subtag, chunk_data):
    uncomp_data = _DecompressChunkData(chunk_data, len(chunk_data))
    with open('E:\\logs\\iPhone\\output\\chunk.bin', 'wb') as f:
        f.write(uncomp_data)
    pos = 0
    tag = int.from_bytes(uncomp_data[pos:pos+4])
    pos += 4
    subtag = int.from_bytes(uncomp_data[pos:pos+4])
    pos += 4
    chunk_len = int.from_bytes(uncomp_data[pos:pos+8])
    pos += 8
    if tag == 0x6001:
        parse_6001_chunk(tag, subtag, uncomp_data[pos:pos+chunk_len])
    else:
        print(f'TAG={hex(tag)}, subtag={hex(subtag)} not support')


def read_chuck(fd):
    buf = fd.read(16)
    tag, subtag, data_length = struct.unpack("<IIQ", buf)
    buf = fd.read(data_length)
    return tag, subtag, buf

fn = "E:\\logs\\iPhone\\iOS14\\1.logarchive\\Persist\\0000000000000016.tracev3"
# fn = "E:\\logs\\iPhone\\1c54319dc1bdb017141bfcf70445764666595478\\log.logarchive\\Persist\\0000000000000001.tracev3"
fd = open(fn, 'rb')
fd.seek(0, os.SEEK_END)
file_size = fd.tell()
fd.seek(0, os.SEEK_SET)
pos = fd.tell()
while pos < file_size:
    _, remainder = divmod(pos, 8)
    if remainder > 0:
        i = 8 - remainder    
        fd.seek(i, os.SEEK_CUR)
        pos += i
    if pos < file_size:
        tag, subtag, chunk_data = read_chuck(fd)
        pos = fd.tell()
        if tag == 0x1000:
            # file header chuck
            parse_header_chunk(tag, subtag, chunk_data)
            pass
        elif tag == 0x600b:
            pass
            # parse_catalog_chunk(tag, subtag, chunk_data)
        elif tag == 0x600d:
            parse_600D_chunk(tag, subtag, chunk_data)
        else:
            print(f'tag={hex(tag)} subtag={hex(subtag)} Not support')
    
fd.close()