import zipfile

with zipfile.ZipFile('d:/DOWNLOAD/Synthesis English_2.0.apk', 'r') as z:
    content = z.read('assets/www/plugins/cordova-sqlite-storage/www/SQLitePlugin.js').decode('utf-8', errors='ignore')
    for line in content.splitlines():
        if 'createFromResource' in line or 'openDatabase' in line or 'createFromLocation' in line:
            print(line.strip())
