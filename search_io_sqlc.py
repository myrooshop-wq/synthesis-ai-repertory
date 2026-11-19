with open('d:/software by me/synthesis homeopathy/build_apk/classes.dex', 'rb') as f:
    d = f.read()

# Search for io/sqlc/SQLiteAndroidDatabase or SQLitePlugin
# Let's see all strings starting with io/sqlc
import re
matches = re.findall(b'io/sqlc/[a-zA-Z0-9_$]+', d)
for m in set(matches):
    print(m)
