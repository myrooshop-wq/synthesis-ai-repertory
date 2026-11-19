with open('d:/software by me/synthesis homeopathy/build_apk/classes.dex', 'rb') as f:
    d = f.read()

# Search for SQLitePlugin.java code
idx = d.find(b'SQLitePlugin.java')
print("SQLitePlugin.java:", idx)
start = max(0, idx - 100)
end = min(len(d), idx + 200)
print(d[start:end])
