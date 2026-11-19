import zipfile

with zipfile.ZipFile('d:/DOWNLOAD/Synthesis English_2.0.apk', 'r') as z:
    for n in z.namelist():
        if n.startswith('res/'):
            if n.endswith('.db') or 'db' in n:
                print(n)
