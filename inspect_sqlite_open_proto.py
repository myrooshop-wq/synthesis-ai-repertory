import zipfile

with zipfile.ZipFile('d:/DOWNLOAD/Synthesis English_2.0.apk', 'r') as z:
    content = z.read('assets/www/plugins/cordova-sqlite-storage/www/SQLitePlugin.js').decode('utf-8', errors='ignore')
    lines = content.splitlines()
    for i, line in enumerate(lines):
        if 'SQLitePlugin.prototype.open =' in line or 'open: function' in line:
            for j in range(max(0, i-5), min(len(lines), i+30)):
                print(f"{j}: {lines[j]}")
            break
