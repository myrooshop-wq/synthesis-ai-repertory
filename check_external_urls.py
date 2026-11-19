with open('static/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

print('static/index.html length:', len(content))
# Check if there are any references to http:// or cdnjs
import re
links = re.findall(r'(?:href|src)=["\']([^"\']+)["\']', content)
print('External URLs in static/index.html:')
for u in set(links):
    if u.startswith('http') or '//' in u:
        print(' -', u)
