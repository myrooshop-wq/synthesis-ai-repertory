import zipfile

with zipfile.ZipFile('d:/DOWNLOAD/Synthesis English_2.0.apk', 'r') as z:
    print(z.read('assets/www/js/libs/android/xapkreader.js').decode('utf-8', errors='ignore'))
