import zipfile

with zipfile.ZipFile('d:/software by me/synthesis homeopathy/release/Synthesis_AI_Repertory_2.0.apk', 'r') as z:
    for n in z.namelist():
        if n.endswith('.db'):
            print(n, z.getinfo(n).file_size)
