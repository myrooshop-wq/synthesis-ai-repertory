import zipfile

with zipfile.ZipFile('d:/DOWNLOAD/Synthesis English_2.0.apk', 'r') as z:
    for n in z.namelist():
        if n.endswith('.js'):
            data = z.read(n).decode('utf-8', errors='ignore')
            if 'assets' in data or 'copy' in data or 'createFrom' in data:
                # check where
                for line in data.splitlines():
                    if 'createFromResource' in line or 'createFromLocation' in line or 'synthesis.202.db' in line:
                        print(f"In {n}: {line.strip()}")
