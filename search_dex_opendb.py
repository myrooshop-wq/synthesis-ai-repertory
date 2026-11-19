with open('d:/software by me/synthesis homeopathy/build_apk/classes.dex', 'rb') as f:
    d = f.read()

# Search for "openDatabase" in classes.dex
idx = 0
while True:
    idx = d.find(b'openDatabase', idx)
    if idx == -1: break
    print(f"Match at {idx}: {d[max(0, idx-50):idx+50]}")
    idx += len(b'openDatabase')
