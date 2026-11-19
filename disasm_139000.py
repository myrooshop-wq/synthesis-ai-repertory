with open('d:/software by me/synthesis homeopathy/build_apk/classes.dex', 'rb') as f:
    d = f.read()

# At 139032: 26 0d f5 0b 6e 20 fc 02 dc 00 (invoke-virtual StringBuilder.append)
# Let's inspect instructions 138980 to 139150 in detail!
# In smali / dalvik:
# v13 = "www/db/"
# invoke-virtual {v12, v13}, StringBuilder.append
# invoke-virtual {v12, v...}, StringBuilder.append
# what was appended before and after?
import struct
for p in range(139000, 139150, 2):
    op = d[p]
    if op == 0x1a:
        s_idx = struct.unpack('<H', d[p+2:p+4])[0]
        print(f"{p}: const-string v{d[p+1]}, s_idx={s_idx}")
    elif op in [0x6e, 0x6f, 0x70, 0x71, 0x72]:
        m_idx = struct.unpack('<H', d[p+2:p+4])[0]
        print(f"{p}: invoke mid={m_idx}")
