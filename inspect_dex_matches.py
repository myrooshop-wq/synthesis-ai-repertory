with open('d:/software by me/synthesis homeopathy/build_apk/classes.dex', 'rb') as f:
    d = f.read()

import re
matches = [m.start() for m in re.finditer(b'be[./]archibel[./]synthesis[./]en', d)]
print("Matches in classes.dex:", len(matches))
for pos in matches:
    print(pos, d[pos-10:pos+40])
