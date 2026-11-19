with open('d:/software by me/synthesis homeopathy/build_apk/classes.dex', 'rb') as f:
    d = f.read()

import struct
string_ids_off = struct.unpack('<I', d[60:64])[0]
def get_str(idx):
    try:
        off = struct.unpack('<I', d[string_ids_off + idx*4 : string_ids_off + (idx+1)*4])[0]
        p = off
        l = 0
        s = 0
        while True:
            b = d[p]
            p += 1
            l |= (b & 0x7f) << s
            if not (b & 0x80): break
            s += 7
        return d[p:p+l].decode('utf-8', errors='ignore')
    except:
        return ''

for pos in range(138900, 139150):
    if d[pos] == 0x1a:
        s_idx = struct.unpack('<H', d[pos+2:pos+4])[0]
        print(f'{pos}: const-string v{d[pos+1]}, "{get_str(s_idx)}"')
