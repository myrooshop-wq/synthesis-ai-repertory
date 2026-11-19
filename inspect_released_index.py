import zipfile

with zipfile.ZipFile('d:/software by me/synthesis homeopathy/release/Synthesis_AI_Repertory_2.0.apk', 'r') as z:
    content = z.read('assets/www/index.html').decode('utf-8', errors='ignore')
    for l in content.splitlines()[:30]:
        print(l)
