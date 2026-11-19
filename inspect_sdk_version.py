import zipfile, struct

with zipfile.ZipFile('d:/DOWNLOAD/Synthesis English_2.0.apk', 'r') as z:
    data = z.read('AndroidManifest.xml')

# Let's search for integers after minSdkVersion (which was string index in string pool)
# In our previous string pool list:
# 6: minSdkVersion
# 11: targetSdkVersion
# 20: compileSdkVersion
print('Length of data:', len(data))
# Let's search for 0x00100102 (START_TAG) or attribute resource IDs
