with open('d:/software by me/synthesis homeopathy/build_apk/classes.dex', 'rb') as f:
    d = f.read()

# Search for "open" or "SQLitePlugin" actions
pos = 0
while True:
    pos = d.find(b'SQLitePlugin', pos)
    if pos == -1: break
    print(f"Match at {pos}: {d[pos-20:pos+80]}")
    pos += len(b'SQLitePlugin')
