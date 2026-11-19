with open('d:/software by me/synthesis homeopathy/ai_repertory.html', 'r', encoding='utf-8') as f:
    text = f.read()

# Let's find toggleSpeechRecording or speech
idx = text.find('toggleSpeechRecording')
print('Speech in ai_repertory.html:')
print(text[idx:idx+800])
