import zipfile, struct

with zipfile.ZipFile('d:/software by me/synthesis homeopathy/release/Synthesis_AI_Repertory_2.0.apk', 'r') as z:
    data = z.read('AndroidManifest.xml')

# String pool
chunk_type, chunk_size = struct.unpack('<II', data[8:16])
string_count, style_count, flags, strings_start, styles_start = struct.unpack('<IIIII', data[16:36])
offsets = [struct.unpack('<I', data[36+i*4:40+i*4])[0] for i in range(string_count)]
strings_data_start = 8 + strings_start
strings = []
is_utf8 = bool(flags & (1 << 8))
for off in offsets:
    pos = strings_data_start + off
    if is_utf8:
        u16len = data[pos]
        pos += 1
        if u16len & 0x80: pos += 1
        u8len = data[pos]
        pos += 1
        if u8len & 0x80: pos += 1
        strings.append(data[pos:pos+u8len].decode('utf-8', errors='ignore'))
    else:
        u16len = struct.unpack('<H', data[pos:pos+2])[0]
        pos += 2
        if u16len & 0x8000: pos += 2
        strings.append(data[pos:pos+u16len*2].decode('utf-16le', errors='ignore'))

for i, s in enumerate(strings):
    if 'be.archibel' in s:
        print(f'{i}: {s}')
