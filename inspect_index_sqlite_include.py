import zipfile

with zipfile.ZipFile('d:/DOWNLOAD/Synthesis English_2.0.apk', 'r') as z:
    content = z.read('assets/www/index.html').decode('utf-8', errors='ignore')
    for line in content.splitlines():
        if 'SQLitePlugin' in line:
            print(line.strip())
