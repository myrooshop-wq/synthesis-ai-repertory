with open('d:/software by me/synthesis homeopathy/build_apk/classes.dex', 'rb') as f:
    d = f.read()

idx = 0
while True:
    idx = d.find(b'202', idx)
    if idx == -1: break
    print(idx, d[max(0, idx-30):idx+30])
    idx += 3
