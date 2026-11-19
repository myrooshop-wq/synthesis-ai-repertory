import zipfile

with zipfile.ZipFile('d:/DOWNLOAD/Synthesis English_2.0.apk', 'r') as z:
    content = z.read('assets/www/js/app.activation.js').decode('utf-8', errors='ignore')
    lines = content.splitlines()
    for i, l in enumerate(lines):
        if 'module.checkStatus = function' in l:
            print(f'Line {i}:')
            for j in range(i, min(len(lines), i+30)):
                print(f'{j}: {lines[j]}')
            break
