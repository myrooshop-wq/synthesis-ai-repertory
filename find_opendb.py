import zipfile

with zipfile.ZipFile('d:/software by me/synthesis homeopathy/release/Synthesis_AI_Repertory_2.0.apk', 'r') as z:
    for n in z.namelist():
        if n.endswith('.js'):
            data = z.read(n).decode('utf-8', errors='ignore')
            if 'openDatabase' in data:
                print('openDatabase in:', n)
