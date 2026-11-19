with open('d:/software by me/synthesis homeopathy/ai_repertory.html', 'r', encoding='utf-8') as f:
    text = f.read()

idx = text.find('function toggleSpeechRecording')
print('Function implementation:')
print(text[idx:idx+900])
