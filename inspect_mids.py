with open('d:/software by me/synthesis homeopathy/build_apk/classes.dex', 'rb') as f:
    d = f.read()

import struct
method_ids_off = struct.unpack('<I', d[88:92])[0]
string_ids_off = struct.unpack('<I', d[60:64])[0]
type_ids_off = struct.unpack('<I', d[68:72])[0]

def get_str(idx):
    off = struct.unpack('<I', d[string_ids_off + idx*4 : string_ids_off + (idx+1)*4])[0]
    p = off
    l = 0; s = 0
    while True:
        b = d[p]; p += 1; l |= (b & 0x7f) << s
        if not (b & 0x80): break
        s += 7
    return d[p:p+l].decode('utf-8', errors='ignore')

def get_method_info(mid):
    class_idx = struct.unpack('<H', d[method_ids_off + mid*8 : method_ids_off + mid*8 + 2])[0]
    name_idx = struct.unpack('<I', d[method_ids_off + mid*8 + 4 : method_ids_off + mid*8 + 8])[0]
    s_idx = struct.unpack('<I', d[type_ids_off + class_idx*4 : type_ids_off + (class_idx+1)*4])[0]
    return f"{get_str(s_idx)}->{get_str(name_idx)}"

for mid in [756, 764, 766, 119, 745, 751]:
    print(mid, get_method_info(mid))
