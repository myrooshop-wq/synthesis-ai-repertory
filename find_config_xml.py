import zipfile

with zipfile.ZipFile('d:/DOWNLOAD/Synthesis English_2.0.apk', 'r') as z:
    for n in z.namelist():
        if 'config.xml' in n.lower():
            print(n)
