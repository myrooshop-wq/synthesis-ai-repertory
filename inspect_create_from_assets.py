with open('d:/software by me/synthesis homeopathy/build_apk/classes.dex', 'rb') as f:
    d = f.read()

idx = d.find(b'createFromAssets')
print("createFromAssets:", idx)
start = max(0, idx - 100)
end = min(len(d), idx + 200)
print(d[start:end])
