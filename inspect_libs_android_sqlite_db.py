import zipfile

with zipfile.ZipFile('d:/DOWNLOAD/Synthesis English_2.0.apk', 'r') as z:
    content = z.read('assets/www/js/libs/android/SQLitePlugin.js').decode('utf-8', errors='ignore')
    for line in content.splitlines():
        if 'createFrom' in line or 'db' in line.lower():
            if len(line.strip()) < 100:
                print(line.strip())
