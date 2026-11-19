import zipfile

with zipfile.ZipFile('d:/DOWNLOAD/Synthesis English_2.0.apk', 'r') as z:
    manifest_bytes = z.read('AndroidManifest.xml')
    print('Manifest size:', len(manifest_bytes))
    # Check strings in manifest
    import re
    strings = re.findall(b'[a-zA-Z0-9_.-]{4,}', manifest_bytes)
    print('Sample manifest strings:', strings[:30])
