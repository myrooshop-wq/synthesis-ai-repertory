import struct

def patch_axml_string(data, old_str, new_str):
    assert len(old_str) == len(new_str), "Lengths must match to preserve byte alignments exactly!"
    old_utf16 = old_str.encode('utf-16le')
    new_utf16 = new_str.encode('utf-16le')
    count = data.count(old_utf16)
    print(f"Replacing {count} occurrences of '{old_str}' with '{new_str}' in UTF-16LE")
    return data.replace(old_utf16, new_utf16)

# Test on AndroidManifest.xml
with open('d:/software by me/synthesis homeopathy/build_apk/AndroidManifest.xml', 'rb') as f:
    manifest_data = f.read()

# 'be.archibel.synthesis.en' is 23 characters!
# 'org.homeoai.synthesis.en' is 23 characters!
new_manifest = patch_axml_string(manifest_data, 'be.archibel.synthesis.en', 'org.homeoai.synthesis.en')

with open('d:/software by me/synthesis homeopathy/build_apk/res/xml/config.xml', 'rb') as f:
    config_data = f.read()

new_config = patch_axml_string(config_data, 'be.archibel.synthesis.en', 'org.homeoai.synthesis.en')
print("AXML patch test passed!")
