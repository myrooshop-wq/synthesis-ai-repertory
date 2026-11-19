with open('static/index.html', 'r', encoding='utf-8') as f:
    text = f.read()

import re
scripts = re.findall(r'<script[\s\S]*?</script>', text)
print(f'Total script tags: {len(scripts)}')
for i, s in enumerate(scripts):
    print(f'Script {i} length: {len(s)}')

styles = re.findall(r'<style[\s\S]*?</style>', text)
print(f'Total style tags: {len(styles)}')
for i, s in enumerate(styles):
    print(f'Style {i} length: {len(s)}')
