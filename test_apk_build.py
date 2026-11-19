import os
import shutil
import zipfile
import subprocess

build_dir = 'd:/software by me/synthesis homeopathy/test_build'
if os.path.exists(build_dir):
    shutil.rmtree(build_dir)
os.makedirs(build_dir)

src_apk = 'd:/DOWNLOAD/Synthesis English_2.0.apk'
print("Extracting test files...")
with zipfile.ZipFile(src_apk, 'r') as z:
    # Extract only first 20 non-db files for quick test
    for info in z.infolist()[:30]:
        z.extract(info, build_dir)

print("Repacking test apk...")
test_out = 'd:/software by me/synthesis homeopathy/test_unsigned.apk'
with zipfile.ZipFile(test_out, 'w') as zout:
    for root, dirs, files in os.walk(build_dir):
        for f in files:
            full_path = os.path.join(root, f)
            rel_path = os.path.relpath(full_path, build_dir).replace('\\', '/')
            zout.write(full_path, rel_path)

print("Testing uber-apk-signer on test_unsigned.apk...")
java_path = r'C:\Program Files\Microsoft\jdk-11.0.32.101-hotspot\bin\java.exe'
signer_jar = 'd:/software by me/synthesis homeopathy/uber-apk-signer.jar'
cmd = [java_path, '-jar', signer_jar, '-a', test_out, '--allowResign', '-o', 'd:/software by me/synthesis homeopathy/test_release']
p = subprocess.run(cmd, capture_output=True, text=True)
print("Signer return code:", p.returncode)
print("Signer output:", p.stdout)
if p.stderr:
    print("Signer stderr:", p.stderr)
