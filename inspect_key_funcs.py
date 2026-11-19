with open('static/index.html', 'r', encoding='utf-8') as f:
    text = f.read()

import re
patterns = ['runExtraction', 'handleRubricSearch', 'expandSubRubrics', 'recalculateMatrix', 'openSynthesisBookView']
for p in patterns:
    idx = text.find(f'function {p}')
    if idx == -1:
        idx = text.find(f'async function {p}')
    if idx != -1:
        print(f'=== {p} ===')
        print(text[idx:idx+800])
        print('...')
