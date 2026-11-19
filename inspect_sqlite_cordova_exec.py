import zipfile

with zipfile.ZipFile('d:/DOWNLOAD/Synthesis English_2.0.apk', 'r') as z:
    content = z.read('assets/www/plugins/cordova-sqlite-storage/www/SQLitePlugin.js').decode('utf-8', errors='ignore')
    lines = content.splitlines()
    for i in range(193, 230):
        print(f"{i}: {lines[i]}")
