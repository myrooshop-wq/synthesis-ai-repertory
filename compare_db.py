import zipfile
import hashlib
import os

with zipfile.ZipFile('d:/DOWNLOAD/Synthesis English_2.0.apk', 'r') as z:
    apk_db_info = z.getinfo('assets/www/db/synthesis.202.db')
    print('APK db size:', apk_db_info.file_size)
    print('Local synthesis.db size:', os.path.getsize('synthesis.db'))
