import os
import shutil
import zipfile
import subprocess

BASE_DIR = r'd:\software by me\synthesis homeopathy'
SOURCE_APK = r'd:\DOWNLOAD\Synthesis English_2.0.apk'
BUILD_DIR = os.path.join(BASE_DIR, 'build_apk')
RELEASE_DIR = os.path.join(BASE_DIR, 'release')
UNSIGNED_APK = os.path.join(BASE_DIR, 'Synthesis_AI_2.0_unsigned.apk')
JAVA_EXE = r'C:\Program Files\Microsoft\jdk-11.0.32.101-hotspot\bin\java.exe'
SIGNER_JAR = os.path.join(BASE_DIR, 'uber-apk-signer.jar')

print("=== 1. PREPARING BUILD DIRECTORY ===")
if os.path.exists(BUILD_DIR):
    shutil.rmtree(BUILD_DIR)
os.makedirs(BUILD_DIR)

if not os.path.exists(RELEASE_DIR):
    os.makedirs(RELEASE_DIR)

print(f"=== 2. EXTRACTING BASE APK ({SOURCE_APK}) ===")
with zipfile.ZipFile(SOURCE_APK, 'r') as z:
    z.extractall(BUILD_DIR)
print(f"Extracted base APK to {BUILD_DIR}")

print("=== 3. COPYING AI REPERTORY ASSETS ===")
# 3a. Copy ai_repertory.html
dest_ai_html = os.path.join(BUILD_DIR, 'assets', 'www', 'ai_repertory.html')
shutil.copyfile(os.path.join(BASE_DIR, 'ai_repertory.html'), dest_ai_html)
print("Copied ai_repertory.html to assets/www/")

# 3b. Copy all.min.css
dest_css = os.path.join(BUILD_DIR, 'assets', 'www', 'css', 'all.min.css')
shutil.copyfile(os.path.join(BASE_DIR, 'all.min.css'), dest_css)
print("Copied all.min.css to assets/www/css/")

# 3c. Copy fa-solid-900.woff2 to webfonts and fonts
dest_webfonts = os.path.join(BUILD_DIR, 'assets', 'www', 'webfonts')
os.makedirs(dest_webfonts, exist_ok=True)
shutil.copyfile(os.path.join(BASE_DIR, 'fa-solid-900.woff2'), os.path.join(dest_webfonts, 'fa-solid-900.woff2'))

dest_fonts = os.path.join(BUILD_DIR, 'assets', 'www', 'fonts')
os.makedirs(dest_fonts, exist_ok=True)
shutil.copyfile(os.path.join(BASE_DIR, 'fa-solid-900.woff2'), os.path.join(dest_fonts, 'fa-solid-900.woff2'))
print("Copied fa-solid-900.woff2 to assets/www/webfonts/ and assets/www/fonts/")

print("=== 4. PATCHING ACTIVATION BYPASS ===")
# Patch app.activation.js
activation_js_path = os.path.join(BUILD_DIR, 'assets', 'www', 'js', 'app.activation.js')
with open(activation_js_path, 'r', encoding='utf-8', errors='ignore') as f:
    act_content = f.read()

# Replace checkStatus definition
old_check_status = "module.checkStatus = function() {"
new_check_status = """module.checkStatus = function() {
			var deferredResult = $.Deferred();
			var activation = App.data.get().activation;
			activation.active = true;
			activation.complete = true;
			App.data.save();
			deferredResult.resolve({ active: true, complete: true, connection: true });
			return deferredResult.promise();
		};
		var _disabled_checkStatus = function() {"""

if old_check_status in act_content:
    act_content = act_content.replace(old_check_status, new_check_status, 1)
    with open(activation_js_path, 'w', encoding='utf-8') as f:
        f.write(act_content)
    print("Patched app.activation.js: permanent activation bypass enabled.")
else:
    print("Warning: could not find module.checkStatus in app.activation.js")

# Patch app.js
app_js_path = os.path.join(BUILD_DIR, 'assets', 'www', 'js', 'app.js')
with open(app_js_path, 'r', encoding='utf-8', errors='ignore') as f:
    app_content = f.read()

# Ensure activation is marked active on save
if "activationData.active" in app_content:
    app_content = app_content.replace("if (!activationData.active) {", "if (false) {")
    with open(app_js_path, 'w', encoding='utf-8') as f:
        f.write(app_content)
    print("Patched app.js: free trial / activation checks bypassed.")

print("=== 5. PATCHING INDEX.HTML NAVIGATION ===")
index_html_path = os.path.join(BUILD_DIR, 'assets', 'www', 'index.html')
with open(index_html_path, 'r', encoding='utf-8', errors='ignore') as f:
    idx_content = f.read()

# 5a. Add launch redirect to ai_repertory.html if not specifically requesting classic view
redirect_script = """
<script type="text/javascript">
  (function() {
    // If not navigating explicitly back to classic view
    if (!window.location.hash && !window.location.search.includes('view=classic')) {
      window.location.replace('ai_repertory.html');
    }
  })();
</script>
"""
idx_content = idx_content.replace('<head>', '<head>\n' + redirect_script, 1)

# 5b. Add prominent banner at top of home-list-1 (Chapters)
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
    print("Added AI Repertory banner to #home-list-1.")

# 5c. Add AI Workstation button in navbars
nav_item_old = '<li><a href="#bookmarksview" data-icon="star" data-applabel="detail_0006">Bookmarks</a></li>'
nav_item_new = '<li><a href="ai_repertory.html" data-icon="star" style="color: #22c55e !important; font-weight: bold;">AI Workstation</a></li>'
idx_content = idx_content.replace(nav_item_old, nav_item_new)
print("Updated navbars with AI Workstation tab.")

with open(index_html_path, 'w', encoding='utf-8') as f:
    f.write(idx_content)

print("=== 6. REPACKING ZIP / APK ===")
if os.path.exists(UNSIGNED_APK):
    os.remove(UNSIGNED_APK)

# In Android APKs, .so files and resources should be stored or deflated. Standard zipfile works with uber-apk-signer as it zip-aligns to 4-byte boundaries.
with zipfile.ZipFile(UNSIGNED_APK, 'w', compression=zipfile.ZIP_DEFLATED) as zout:
    for root, dirs, files in os.walk(BUILD_DIR):
        for f in files:
            full_path = os.path.join(root, f)
            rel_path = os.path.relpath(full_path, BUILD_DIR).replace('\\', '/')
            # If native library, store uncompressed
            if rel_path.endswith('.so'):
                zout.write(full_path, rel_path, compress_type=zipfile.ZIP_STORED)
            else:
                zout.write(full_path, rel_path, compress_type=zipfile.ZIP_DEFLATED)

print(f"Repacked unsigned APK to {UNSIGNED_APK} (Size: {os.path.getsize(UNSIGNED_APK):,} bytes)")

print("=== 7. SIGNING AND ZIPALIGNING WITH UBER-APK-SIGNER ===")
cmd = [
    JAVA_EXE, '-jar', SIGNER_JAR,
    '-a', UNSIGNED_APK,
    '--allowResign',
    '-o', RELEASE_DIR
]
proc = subprocess.run(cmd, capture_output=True, text=True)
print("Signer stdout:\n", proc.stdout)
if proc.stderr:
    print("Signer stderr:\n", proc.stderr)

print("=== 8. VERIFYING SIGNED APK ===")
verify_cmd = [
    JAVA_EXE, '-jar', SIGNER_JAR,
    '-y',
    '-a', os.path.join(RELEASE_DIR, 'Synthesis_AI_2.0_unsigned-aligned-debugSigned.apk')
]
proc_v = subprocess.run(verify_cmd, capture_output=True, text=True)
print("Verification stdout:\n", proc_v.stdout)

# Clean rename to friendly name
final_apk_path = os.path.join(RELEASE_DIR, 'Synthesis_AI_Repertory_2.0.apk')
debug_signed_apk = os.path.join(RELEASE_DIR, 'Synthesis_AI_2.0_unsigned-aligned-debugSigned.apk')
if os.path.exists(debug_signed_apk):
    if os.path.exists(final_apk_path):
        os.remove(final_apk_path)
    os.rename(debug_signed_apk, final_apk_path)
    print(f"\nSUCCESS! Final installable APK created:\n{final_apk_path}\nSize: {os.path.getsize(final_apk_path):,} bytes")
