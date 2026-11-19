with open('temp_apk_work/assets/www/index.html', 'r', encoding='utf-8', errors='ignore') as f:
    lines = f.readlines()

for i, l in enumerate(lines):
    if 'data-role="navbar"' in l or "data-role='navbar'" in l:
        print(f"Line {i}: {l.strip()}")
        # print next 10 lines
        for j in range(i+1, min(i+12, len(lines))):
            print(f"   {lines[j].strip()}")
            if '</div>' in lines[j]:
                break
