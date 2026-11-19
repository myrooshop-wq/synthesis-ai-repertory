with open('d:/software by me/synthesis homeopathy/build_apk/classes.dex', 'rb') as f:
    d = f.read()

# Search for SQLitePlugin methods or strings
for target in [b'createFromResource', b'openDatabase', b'getDatabasePath', b'databases']:
    idx = 0
    while True:
        idx = d.find(target, idx)
        if idx == -1: break
        print(f"Found {target} at {idx}: {d[max(0, idx-20):idx+len(target)+30]}")
        idx += len(target)
