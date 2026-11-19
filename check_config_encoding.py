with open('d:/software by me/synthesis homeopathy/build_apk/res/xml/config.xml', 'rb') as f:
    d = f.read()

print('utf8 count in config.xml:', d.count(b'be.archibel.synthesis.en'))
print('utf16 count in config.xml:', d.count('be.archibel.synthesis.en'.encode('utf-16le')))
