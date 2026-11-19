import zipfile

with zipfile.ZipFile('d:/DOWNLOAD/Synthesis English_2.0.apk', 'r') as z:
    for n in z.namelist():
        if not n.endswith('.png') and not n.endswith('.gif') and not n.endswith('.jpg') and not n.endswith('.db') and not n.endswith('.so'):
            data = z.read(n)
            if b'synthesis.202' in data:
                print(f"Binary match in: {n}")
