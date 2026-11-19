with open('d:/software by me/synthesis homeopathy/build_apk/classes.dex', 'rb') as f:
    d = f.read()

import re
matches = re.findall(b'www/db/[a-zA-Z0-9_.-]+', d)
print('matches in classes.dex:', matches)

matches2 = re.findall(b'[a-zA-Z0-9_.-]+\\.db', d)
print('matches2 in classes.dex:', set(matches2))
