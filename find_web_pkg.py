import zipfile

with zipfile.ZipFile('d:/software by me/synthesis homeopathy/release/Synthesis_AI_Repertory_2.0.apk', 'r') as z:
    for n in z.namelist():
        if 'synthesis' in n and (n.endswith('.js') or n.endswith('.html')):
            d = z.read(n).decode('utf-8', errors='ignore')
            if 'be.archibel' in d:
                print('Found in', n)
