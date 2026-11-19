with open('d:/software by me/synthesis homeopathy/build_apk/classes.dex', 'rb') as f:
    d = f.read()

# Search for "createFromResource" and nearby strings or code
idx = d.find(b'createFromResource')
start = max(0, idx - 200)
end = min(len(d), idx + 200)
print(d[start:end])
