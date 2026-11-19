import zipfile, struct

with zipfile.ZipFile('d:/DOWNLOAD/Synthesis English_2.0.apk', 'r') as z:
    data = z.read('AndroidManifest.xml')

# Find string pool strings first
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

# Parse chunks after string pool
pos = 8 + chunk_size
while pos < len(data):
    ch_type, ch_size = struct.unpack('<II', data[pos:pos+8])
    if ch_type == 0x00100102: # START_TAG
        line_num, comment, ns, name, attr_start, attr_size, attr_count, id_idx, class_idx, style_idx = struct.unpack('<IIIIHHHHHH', data[pos+8:pos+36])
        tag_name = strings[name] if name < len(strings) else f'str_{name}'
        attr_pos = pos + 36
        attrs = []
        for a in range(attr_count):
            a_ns, a_name, a_val_str, a_type, a_data = struct.unpack('<IIIII', data[attr_pos:attr_pos+20])
            a_name_str = strings[a_name] if a_name < len(strings) else f'str_{a_name}'
            attrs.append((a_name_str, a_val_str, a_type, a_data))
            attr_pos += 20
        print(f'Tag: {tag_name}, attrs: {attrs}')
    pos += ch_size
