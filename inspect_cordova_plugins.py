import zipfile

with zipfile.ZipFile('d:/DOWNLOAD/Synthesis English_2.0.apk', 'r') as z:
    content = z.read('assets/www/cordova_plugins.js').decode('utf-8', errors='ignore')
    print(content)
