import zipfile

with zipfile.ZipFile('d:/DOWNLOAD/Synthesis English_2.0.apk', 'r') as z:
    for n in z.namelist():
        if n.endswith('.js'):
            data = z.read(n).decode('utf-8', errors='ignore')
            if 'www/db' in data or 'synthesis.202' in data:
                print(f"Found in {n}!")
                for l in data.splitlines():
                    if '202' in l or 'www/db' in l:
                        print("  ", l.strip()[:100])
