with open('d:/software by me/synthesis homeopathy/build_apk/classes.dex', 'rb') as f:
    d = f.read()

# Search for "createFromResource" and see the class around it
idx = 0
while True:
    idx = d.find(b'createFromResource', idx)
    if idx == -1: break
    print(f"Match at {idx}: {d[max(0, idx-100):idx+100]}")
    idx += len(b'createFromResource')
