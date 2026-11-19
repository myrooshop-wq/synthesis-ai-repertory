with open('d:/software by me/synthesis homeopathy/build_apk/classes.dex', 'rb') as f:
    d = f.read()

# Search for "synthesis" in classes.dex
idx = 0
while True:
    idx = d.find(b'synthesis', idx)
    if idx == -1: break
    print(f"Position {idx}: {d[max(0, idx-40):idx+60]}")
    idx += len(b'synthesis')
