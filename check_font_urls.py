with open('all.min.css', 'r', encoding='utf-8') as f:
    text = f.read()

import re
urls = re.findall(r'url\([^)]+\)', text)
print('Font URLs in all.min.css:')
for u in set(urls):
    print(' ', u)
