import struct
d = open('d:/software by me/synthesis homeopathy/build_apk/classes.dex', 'rb').read()
method_ids_off = struct.unpack('<I', d[88:92])[0]
method_ids_size = struct.unpack('<I', d[84:88])[0]
print("method_ids_off:", method_ids_off, "method_ids_size:", method_ids_size)
