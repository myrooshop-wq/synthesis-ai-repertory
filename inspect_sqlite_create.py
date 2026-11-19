import zipfile

with zipfile.ZipFile('d:/software by me/synthesis homeopathy/release/Synthesis_AI_Repertory_2.0.apk', 'r') as z:
    lines = z.read('assets/www/plugins/cordova-sqlite-storage/www/SQLitePlugin.js').decode('utf-8', errors='ignore').splitlines()

for i, l in enumerate(lines):
    if 'createFrom' in l:
        for j in range(max(0, i-5), min(len(lines), i+20)):
            print(f'{j}: {lines[j]}')
        break
