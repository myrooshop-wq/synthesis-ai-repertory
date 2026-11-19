with open('static/index.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print('Total lines in static/index.html:', len(lines))
# Let's inspect lines 1 to 150
for i in range(min(70, len(lines))):
    print(f'{i+1}: {lines[i].rstrip()}')
