import os
import shutil
import zipfile
import subprocess
import zlib
import hashlib
import struct

BASE_DIR = r'd:\software by me\synthesis homeopathy'
SOURCE_APK = r'd:\DOWNLOAD\Synthesis English_2.0.apk'
BUILD_DIR = os.path.join(BASE_DIR, 'build_apk')
RELEASE_DIR = os.path.join(BASE_DIR, 'release')
UNSIGNED_APK = os.path.join(BASE_DIR, 'Synthesis_AI_2.0_unsigned.apk')
FINAL_APK = os.path.join(RELEASE_DIR, 'Synthesis_AI_Repertory_2.0.apk')
JAVA_EXE = r'C:\Program Files\Microsoft\jdk-11.0.32.101-hotspot\bin\java.exe'
SIGNER_JAR = os.path.join(BASE_DIR, 'uber-apk-signer.jar')

OLD_PKG = b'be.archibel.synthesis.en'
NEW_PKG = b'org.homeoai.synthesis.en'

print("=== 1. PREPARING BUILD DIRECTORY ===")
if os.path.exists(BUILD_DIR):
    shutil.rmtree(BUILD_DIR)
os.makedirs(BUILD_DIR)
os.makedirs(RELEASE_DIR, exist_ok=True)

print(f"=== 2. EXTRACTING BASE APK ({SOURCE_APK}) ===")
with zipfile.ZipFile(SOURCE_APK, 'r') as z:
    z.extractall(BUILD_DIR)

print("=== 3. FIXING PRE-POPULATED DATABASE IN ASSETS ===")
# SQLitePlugin looks for www/db/{dbname} where dbname is 'synthesis' or 'synthesis.202.db'.
# We copy synthesis.202.db to both 'assets/www/db/synthesis' and 'assets/www/db/synthesis.db'
src_db = os.path.join(BUILD_DIR, 'assets', 'www', 'db', 'synthesis.202.db')
dest_synthesis = os.path.join(BUILD_DIR, 'assets', 'www', 'db', 'synthesis')
dest_synthesis_db = os.path.join(BUILD_DIR, 'assets', 'www', 'db', 'synthesis.db')
shutil.copyfile(src_db, dest_synthesis)
shutil.copyfile(src_db, dest_synthesis_db)
print("Configured pre-populated databases: 'synthesis' and 'synthesis.db'.")

print("=== 4. COPYING ASSETS & FONT-AWESOME ===")
dest_ai_html = os.path.join(BUILD_DIR, 'assets', 'www', 'ai_repertory.html')
shutil.copyfile(os.path.join(BASE_DIR, 'ai_repertory.html'), dest_ai_html)

dest_css = os.path.join(BUILD_DIR, 'assets', 'www', 'css', 'all.min.css')
shutil.copyfile(os.path.join(BASE_DIR, 'all.min.css'), dest_css)

dest_webfonts = os.path.join(BUILD_DIR, 'assets', 'www', 'webfonts')
os.makedirs(dest_webfonts, exist_ok=True)
shutil.copyfile(os.path.join(BASE_DIR, 'fa-solid-900.woff2'), os.path.join(dest_webfonts, 'fa-solid-900.woff2'))

dest_fonts = os.path.join(BUILD_DIR, 'assets', 'www', 'fonts')
os.makedirs(dest_fonts, exist_ok=True)
shutil.copyfile(os.path.join(BASE_DIR, 'fa-solid-900.woff2'), os.path.join(dest_fonts, 'fa-solid-900.woff2'))

print("=== 5. PATCHING SPLASHSCREEN & REDIRECT ===")
# In index.html, we must hide the splashscreen before navigating to ai_repertory.html so it doesn't get stuck!
index_html_path = os.path.join(BUILD_DIR, 'assets', 'www', 'index.html')
with open(index_html_path, 'r', encoding='utf-8', errors='ignore') as f:
    idx_content = f.read()

# Replace onDeviceReady in index.html to hide splashscreen and launch ai_repertory.html seamlessly
old_deviceready = """document.addEventListener("deviceready", function() {
console.log("onDeviceReady ok");
App.load(); // entry point
window.open = cordova.InAppBrowser.open;
}, false);"""

new_deviceready = """document.addEventListener("deviceready", function() {
    console.log("onDeviceReady ok");
    if (navigator.splashscreen && navigator.splashscreen.hide) {
        navigator.splashscreen.hide();
    }
    window.open = cordova.InAppBrowser.open;
    if (!window.location.hash && !window.location.search.includes('view=classic')) {
        window.location.replace('ai_repertory.html');
        return;
    }
    App.load();
}, false);"""

if old_deviceready in idx_content:
    idx_content = idx_content.replace(old_deviceready, new_deviceready, 1)
    print("Replaced deviceready in index.html: splashscreen hide + clean redirect.")
else:
    print("Warning: old_deviceready pattern not found exactly.")

# Add top banner in #home-list-1
banner_html = """
	<div style="background: linear-gradient(135deg, #108a00, #047857); padding: 12px 16px; margin: 8px 10px; border-radius: 8px; color: white; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 4px 10px rgba(0,0,0,0.25); cursor: pointer;" onclick="window.location.href='ai_repertory.html'">
		<div style="display:flex; align-items:center; gap:10px;">
			<span style="font-size:22px;">✨</span>
			<div>
				<div style="font-size: 15px; font-weight: bold; color: white;">AI Repertory & Consultation</div>
				<div style="font-size: 11px; opacity: 0.9; color: #eaf6ea;">Voice dictation, semantic search, rubrics grid & repertorisation</div>
			</div>
		</div>
		<a href="ai_repertory.html" class="ui-btn ui-btn-inline ui-corner-all ui-mini" style="background: white; color: #108a00 !important; font-weight: bold; border:none; padding:6px 12px; margin:0;">OPEN &rarr;</a>
	</div>
"""
target_page = '<div data-role="page" id="home-list-1" data-theme="b">'
if target_page in idx_content:
    idx_content = idx_content.replace(target_page, target_page + '\n' + banner_html, 1)

with open(index_html_path, 'w', encoding='utf-8') as f:
    f.write(idx_content)

print("=== 6. PATCHING ACTIVATION BYPASS ===")
act_path = os.path.join(BUILD_DIR, 'assets', 'www', 'js', 'app.activation.js')
with open(act_path, 'r', encoding='utf-8', errors='ignore') as f:
    act_content = f.read()

old_check = "module.checkStatus = function() {"
new_check = """module.checkStatus = function() {
			var deferredResult = $.Deferred();
			var activation = App.data.get().activation;
			activation.active = true;
			activation.complete = true;
			App.data.save();
			deferredResult.resolve({ active: true, complete: true, connection: true });
			return deferredResult.promise();
		};
		var _disabled_checkStatus = function() {"""
act_content = act_content.replace(old_check, new_check, 1)
with open(act_path, 'w', encoding='utf-8') as f:
    f.write(act_content)

appjs_path = os.path.join(BUILD_DIR, 'assets', 'www', 'js', 'app.js')
with open(appjs_path, 'r', encoding='utf-8', errors='ignore') as f:
    app_content = f.read()
app_content = app_content.replace("if (!activationData.active) {", "if (false) {")
with open(appjs_path, 'w', encoding='utf-8') as f:
    f.write(app_content)

print("=== 7. STANDALONE APP IDENTITY: PATCHING PACKAGE NAME ===")
# 7a. AndroidManifest.xml (UTF-16LE in String Pool)
manifest_path = os.path.join(BUILD_DIR, 'AndroidManifest.xml')
with open(manifest_path, 'rb') as f:
    m_bytes = f.read()
m_bytes = m_bytes.replace(OLD_PKG.decode('latin1').encode('utf-16le'), NEW_PKG.decode('latin1').encode('utf-16le'))
with open(manifest_path, 'wb') as f:
    f.write(m_bytes)
print("Patched AndroidManifest.xml package name to org.homeoai.synthesis.en")

# 7b. res/xml/config.xml (UTF-8)
config_path = os.path.join(BUILD_DIR, 'res', 'xml', 'config.xml')
with open(config_path, 'rb') as f:
    c_bytes = f.read()
c_bytes = c_bytes.replace(OLD_PKG, NEW_PKG)
with open(config_path, 'wb') as f:
    f.write(c_bytes)
print("Patched config.xml package name to org.homeoai.synthesis.en")

# 7c. classes.dex
dex_path = os.path.join(BUILD_DIR, 'classes.dex')
with open(dex_path, 'rb') as f:
    d_bytes = f.read()

old_slash = OLD_PKG.replace(b'.', b'/')
new_slash = NEW_PKG.replace(b'.', b'/')
d_arr = bytearray(d_bytes)
d_arr = bytearray(bytes(d_arr).replace(OLD_PKG, NEW_PKG))
d_arr = bytearray(bytes(d_arr).replace(old_slash, new_slash))

# Recalculate SHA-1 signature
sha1 = hashlib.sha1(d_arr[32:]).digest()
d_arr[12:32] = sha1

# Recalculate Adler32 checksum
adler = zlib.adler32(d_arr[12:]) & 0xffffffff
d_arr[8:12] = struct.pack('<I', adler)

with open(dex_path, 'wb') as f:
    f.write(d_arr)
print("Patched classes.dex with recalculation of SHA1 and Adler32.")

print("=== 8. ENHANCING AI_REPERTORY.HTML FOR SPEECH & DATABASE ===")
ai_html_path = os.path.join(BUILD_DIR, 'assets', 'www', 'ai_repertory.html')
with open(ai_html_path, 'r', encoding='utf-8') as f:
    ai_content = f.read()

# Make sure splashscreen is hidden when ai_repertory.html loads
ai_content = ai_content.replace(
    'document.addEventListener(\'deviceready\', function() {',
    '''document.addEventListener('deviceready', function() {
      if (navigator.splashscreen && navigator.splashscreen.hide) {
        navigator.splashscreen.hide();
      }'''
)

with open(ai_html_path, 'w', encoding='utf-8') as f:
    f.write(ai_content)

print("=== 9. COMPRESSING REPACKED APK ===")
if os.path.exists(UNSIGNED_APK):
    os.remove(UNSIGNED_APK)

with zipfile.ZipFile(UNSIGNED_APK, 'w', compression=zipfile.ZIP_DEFLATED) as zout:
    for root, dirs, files in os.walk(BUILD_DIR):
        for f in files:
            full_path = os.path.join(root, f)
            rel_path = os.path.relpath(full_path, BUILD_DIR).replace('\\', '/')
            if rel_path.endswith('.so'):
                zout.write(full_path, rel_path, compress_type=zipfile.ZIP_STORED)
            else:
                zout.write(full_path, rel_path, compress_type=zipfile.ZIP_DEFLATED)

print(f"Repacked APK created: {UNSIGNED_APK} ({os.path.getsize(UNSIGNED_APK):,} bytes)")

print("=== 10. SIGNING & ALIGNING WITH UBER-APK-SIGNER ===")
cmd = [
    JAVA_EXE, '-jar', SIGNER_JAR,
    '-a', UNSIGNED_APK,
    '--allowResign',
    '-o', RELEASE_DIR
]
proc = subprocess.run(cmd, capture_output=True, text=True)
print(proc.stdout)
if proc.stderr:
    print("Signer stderr:", proc.stderr)

debug_signed = os.path.join(RELEASE_DIR, 'Synthesis_AI_2.0_unsigned-aligned-debugSigned.apk')
if os.path.exists(debug_signed):
    if os.path.exists(FINAL_APK):
        os.remove(FINAL_APK)
    os.rename(debug_signed, FINAL_APK)
    print(f"\nBUILD COMPLETE! Installable standalone APK:\n{FINAL_APK}\nSize: {os.path.getsize(FINAL_APK):,} bytes")
