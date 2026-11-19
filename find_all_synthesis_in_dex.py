with open('d:/software by me/synthesis homeopathy/build_apk/classes.dex', 'rb') as f:
    d = f.read()

# Search for "synthesis" in classes.dex
# We found "synthesis" in classes.dex earlier:
idx = 0
while True:
    idx = d.find(b'synthesis', idx)
    if idx == -1: break
    print(idx, d[max(0, idx-20):idx+30])
    idx += len(b'synthesis')
