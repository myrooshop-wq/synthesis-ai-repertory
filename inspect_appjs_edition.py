import zipfile

with zipfile.ZipFile('d:/software by me/synthesis homeopathy/release/Synthesis_AI_Repertory_2.0.apk', 'r') as z:
    lines = z.read('assets/www/js/app.js').decode('utf-8', errors='ignore').splitlines()

for i, l in enumerate(lines[:50]):
    if 'edition' in l.lower():
        for j in range(max(0, i-2), min(len(lines), i+30)):
            print(f"{j}: {lines[j]}")
        break
