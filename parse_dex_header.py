import struct
d = open('d:/software by me/synthesis homeopathy/build_apk/classes.dex', 'rb').read()
header_fields = [
    ("magic", 8),
    ("checksum", 4),
    ("signature", 20),
    ("file_size", 4),
    ("header_size", 4),
    ("endian_tag", 4),
    ("link_size", 4),
    ("link_off", 4),
    ("map_off", 4),
    ("string_ids_size", 4),
    ("string_ids_off", 4),
    ("type_ids_size", 4),
    ("type_ids_off", 4),
    ("proto_ids_size", 4),
    ("proto_ids_off", 4),
    ("field_ids_size", 4),
    ("field_ids_off", 4),
    ("method_ids_size", 4),
    ("method_ids_off", 4),
    ("class_defs_size", 4),
    ("class_defs_off", 4),
    ("data_size", 4),
    ("data_off", 4),
]
off = 0
for name, size in header_fields:
    if size == 4:
        val = struct.unpack('<I', d[off:off+4])[0]
        print(f"{name}: {val} (0x{val:x})")
    elif size == 8:
        print(f"{name}: {d[off:off+8]}")
    off += size
