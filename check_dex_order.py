import struct
with open('d:/software by me/synthesis homeopathy/build_apk/classes.dex', 'rb') as f:
    d = f.read()

type_ids_off = 12408
string_ids_off = 112
def get_str(idx):
    off = struct.unpack('<I', d[string_ids_off + idx*4 : string_ids_off + (idx+1)*4])[0]
    p = off; l = 0; s = 0
    while True:
        b = d[p]; p += 1; l |= (b & 0x7f) << s
        if not (b & 0x80): break
        s += 7
    return d[p:p+l].decode('utf-8', errors='ignore')

prev = ''
for i in range(450):
    sid = struct.unpack('<I', d[type_ids_off + i*4 : type_ids_off + (i+1)*4])[0]
    s = get_str(sid)
    if s < prev:
        print(f"OUT OF ORDER at type_id {i}: '{s}' was after '{prev}'")
    prev = s

print("Type table order check complete.")
