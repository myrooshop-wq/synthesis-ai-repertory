with open('temp_apk_work/assets/www/index.html', 'r', encoding='utf-8', errors='ignore') as f:
    lines = f.readlines()

for i in range(130, 160):
    print(f'{i+1}: {lines[i].rstrip()}')
