import struct
import zlib
import hashlib

def patch_dex_package(dex_data, old_pkg, new_pkg):
    assert len(old_pkg) == len(new_pkg)
    old_slash = old_pkg.replace(b'.', b'/')
    new_slash = new_pkg.replace(b'.', b'/')
    
    # 1. Replace strings
    data = bytearray(dex_data)
    data = bytearray(bytes(data).replace(old_pkg, new_pkg))
    data = bytearray(bytes(data).replace(old_slash, new_slash))
    
    # 2. Recalculate SHA-1 signature (bytes 12..32, over bytes 32..end)
    sha1 = hashlib.sha1(data[32:]).digest()
    data[12:32] = sha1
    
    # 3. Recalculate Adler32 checksum (bytes 8..12, over bytes 12..end)
    adler = zlib.adler32(data[12:]) & 0xffffffff
    data[8:12] = struct.pack('<I', adler)
    
    return bytes(data)

with open('d:/software by me/synthesis homeopathy/build_apk/classes.dex', 'rb') as f:
    dex_orig = f.read()

dex_patched = patch_dex_package(dex_orig, b'be.archibel.synthesis.en', b'org.homeoai.synthesis.en')
print("Patched classes.dex successfully, length:", len(dex_patched))
