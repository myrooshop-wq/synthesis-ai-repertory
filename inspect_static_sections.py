with open('static/index.html', 'r', encoding='utf-8') as f:
    text = f.read()

print('Length of static/index.html:', len(text))
print('Sections in static/index.html:')
for line in text.splitlines():
    if '<section' in line or 'id=' in line and ('step' in line.lower() or 'search' in line.lower() or 'rubric' in line.lower() or 'popup' in line.lower()):
        print('  ', line.strip()[:100])
