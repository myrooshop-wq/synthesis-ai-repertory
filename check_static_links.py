with open('static/index.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, l in enumerate(lines[:60]):
    if '<link' in l or '<script' in l:
        print(f'{i}: {l.strip()}')
