import struct
d = open('d:/software by me/synthesis homeopathy/build_apk/classes.dex', 'rb').read()
string_ids_off = struct.unpack('<I', d[60:64])[0]
def get_str(idx):
    off = struct.unpack('<I', d[string_ids_off + idx*4 : string_ids_off + (idx+1)*4])[0]
    p = off
    l = 0; s = 0
    while True:
        b = d[p]; p += 1; l |= (b & 0x7f) << s
        if not (b & 0x80): break
        s += 7
    return d[p:p+l].decode('utf-8', errors='ignore')

# 139166 had createFromAssets (string index)
# What string was at 139200-139300?
for p in range(139150, 139350):
    if d[p] == 0x1a:
        s_idx = struct.unpack('<H', d[p+2:p+4])[0]
        print(p, get_str(s_idx))
