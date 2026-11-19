with open('d:/software by me/synthesis homeopathy/build_apk/classes.dex', 'rb') as f:
    d = f.read()

# Search for "createFrom" in dex
pos = 0
while True:
    pos = d.find(b'createFrom', pos)
    if pos == -1: break
    print(f"Match at {pos}: {d[pos-20:pos+60]}")
    pos += len(b'createFrom')
