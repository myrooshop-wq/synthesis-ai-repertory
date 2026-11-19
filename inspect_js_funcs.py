with open('static/index.html', 'r', encoding='utf-8') as f:
    text = f.read()

import re
funcs = re.findall(r'function\s+([a-zA-Z0-9_]+)\s*\(', text)
print('Functions in static/index.html:')
for fn in funcs:
    print(' -', fn)

async_funcs = re.findall(r'async\s+function\s+([a-zA-Z0-9_]+)\s*\(', text)
print('Async functions:')
for fn in async_funcs:
    print(' -', fn)
