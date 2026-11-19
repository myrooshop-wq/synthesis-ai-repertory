with open('d:/software by me/synthesis homeopathy/build_apk/classes.dex', 'rb') as f:
    d = f.read()

import re
matches = re.findall(b'www/db', d)
print('matches in dex:', len(matches))

# Let's search for openDatabase or createFrom in SQLitePlugin
matches2 = re.findall(b'[a-zA-Z0-9_/]*SQLite[a-zA-Z0-9_/]*', d)
for m in set(matches2):
    if len(m) > 10:
        print(m)
