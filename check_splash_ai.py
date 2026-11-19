with open('d:/software by me/synthesis homeopathy/ai_repertory.html', 'r', encoding='utf-8') as f:
    text = f.read()

import re
matches = [m.start() for m in re.finditer(r'splashscreen', text, re.IGNORECASE)]
print("splashscreen in ai_repertory.html:", len(matches))
for m in matches:
    print(text[m-20:m+40])
