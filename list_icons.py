import zipfile
import re

z = zipfile.ZipFile('d:/DOWNLOAD/Synthesis English_2.0.apk')
html = z.read('assets/www/index.html').decode('utf-8', errors='ignore')
icons = set(re.findall(r'data-icon="([^"]+)"', html))
print("Available icons in original jQuery Mobile theme:", icons)
