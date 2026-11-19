with open('d:/software by me/synthesis homeopathy/build_apk/classes.dex', 'rb') as f:
    d = f.read()

# Search for any string ending in .db or containing db
import re
matches = re.findall(b'assets[a-zA-Z0-9_./-]*', d)
for m in set(matches):
    print(m)
