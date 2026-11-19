import zipfile

with zipfile.ZipFile('d:/DOWNLOAD/Synthesis English_2.0.apk', 'r') as z:
    content = z.read('assets/www/js/app.search.js').decode('utf-8', errors='ignore')
    for l in content.splitlines():
        if 'executeSql' in l or 'SELECT' in l:
            print(l.strip()[:120])
