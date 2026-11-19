import zipfile

with zipfile.ZipFile('d:/DOWNLOAD/Synthesis English_2.0.apk', 'r') as z:
    b = z.read('AndroidManifest.xml')
    print('First 100 bytes:', list(b[:100]))
