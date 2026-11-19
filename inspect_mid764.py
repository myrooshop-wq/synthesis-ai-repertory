import struct
d = open('d:/software by me/synthesis homeopathy/build_apk/classes.dex', 'rb').read()
method_ids_off = struct.unpack('<I', d[88:92])[0]
string_ids_off = struct.unpack('<I', d[60:64])[0]
type_ids_off = struct.unpack('<I', d[68:72])[0]

# method_id_item in dex is:
# class_idx: ushort (2 bytes)
# proto_idx: ushort (2 bytes)
# name_idx: uint (4 bytes)
mid = 764
m_off = method_ids_off + mid*8
c_idx, p_idx, n_idx = struct.unpack('<HHI', d[m_off:m_off+8])
print(f"mid 764: c_idx={c_idx}, p_idx={p_idx}, n_idx={n_idx}")

# read string for n_idx
s_off = struct.unpack('<I', d[string_ids_off + n_idx*4 : string_ids_off + (n_idx+1)*4])[0]
pos = s_off
l = 0; s = 0
while True:
    b = d[pos]; pos += 1; l |= (b & 0x7f) << s
    if not (b & 0x80): break
    s += 7
print("mid 764 name:", d[pos:pos+l].decode('utf-8', errors='ignore'))
