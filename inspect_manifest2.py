import zipfile

with zipfile.ZipFile('d:/DOWNLOAD/Synthesis English_2.0.apk', 'r') as z:
    b = z.read('AndroidManifest.xml')
    # find utf-16le strings
    s = b.decode('latin-1')
    import re
    # print characters that are printable
    clean = "".join([c if 32 <= ord(c) < 127 else " " for c in s])
    words = [w for w in clean.split() if len(w) > 3]
    print('Words in AndroidManifest:', words[:50])
