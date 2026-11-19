with open('d:/software by me/synthesis homeopathy/build_apk/classes.dex', 'rb') as f:
    d = f.read()

# Search for "synthesis" in classes.dex
idx = d.find(b'www/db/')
print(idx, d[idx-20:idx+40])
