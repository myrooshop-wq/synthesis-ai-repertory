import os
import requests
import json
import time

apk_path = r'd:\software by me\synthesis homeopathy\release\Synthesis_AI_Repertory_2.0.apk'
file_size = os.path.getsize(apk_path)
print(f"Uploading APK: {apk_path} ({file_size:,} bytes / {file_size / (1024*1024):.2f} MB)...")

# Get server
server_res = requests.get('https://api.gofile.io/servers')
servers = server_res.json()['data']['servers']
best_server = servers[0]['name']
print(f"Selected Gofile server: {best_server}")

upload_url = f'https://{best_server}.gofile.io/contents/uploadfile'

t0 = time.time()
with open(apk_path, 'rb') as f:
    files = {'file': ('Synthesis_AI_Repertory_2.0.apk', f, 'application/vnd.android.package-archive')}
    res = requests.post(upload_url, files=files)

elapsed = time.time() - t0
print(f"Upload completed in {elapsed:.1f} seconds. Status: {res.status_code}")

data = res.json()
print("Response JSON:")
print(json.dumps(data, indent=2))

if data.get('status') == 'ok':
    download_page = data['data']['downloadPage']
    print("\n" + "="*50)
    print("GOFILE DOWNLOAD LINK:")
    print(download_page)
    print("="*50 + "\n")
else:
    print("Upload failed or unexpected response.")
