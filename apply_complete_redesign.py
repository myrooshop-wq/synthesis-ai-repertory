# apply_complete_redesign.py
import re

with open('index.html', 'r', encoding='utf-8') as f:
    c = f.read()

# 1. Restore clean Google live speech dictation button
p_mic = c.find('<div style="display: flex; gap: 6px; align-items: center; width: 100%;">')
if p_mic != -1:
    p_mic_end = c.find('</select>\n          </div>', p_mic)
    if p_mic_end != -1:
        clean_mic = '''<button class="btn btn-primary" id="micBtn" onclick="toggleSpeechRecording()">
            <i class="fa-solid fa-microphone"></i> <span id="micLabel">Start Dictation (Hindi/English)</span>
          </button>'''
        c = c[:p_mic] + clean_mic + c[p_mic_end + len('</select>\n          </div>'):]
        print('Restored clean mic button')

# 2. Restore original marvelous Google Speech Recognition
speech_func = '''    function toggleSpeechRecording() {
      const btn = document.getElementById('micBtn');
      const label = document.getElementById('micLabel');

      if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
        alert("Speech recognition is not supported in this browser. Please use Chrome/Edge or type directly.");
        return;
      }

      if (isRecording) {
        if (speechRecognition) speechRecognition.stop();
        isRecording = false;
        btn.classList.remove('btn-mic-active');
        label.textContent = "Start Dictation (Hindi/English)";
      } else {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        speechRecognition = new SpeechRecognition();
        speechRecognition.continuous = true;
        speechRecognition.interimResults = true;
        speechRecognition.lang = 'hi-IN'; // Built-in Google Live Speech Recognition (handles Hindi, English, and Hinglish flawlessly)

        speechRecognition.onresult = (event) => {
          let interim = '';
          for (let i = event.resultIndex; i < event.results.length; ++i) {
            if (event.results[i].isFinal) {
              const textChunk = event.results[i][0].transcript;
              const area = document.getElementById('consultationText');
              area.value = (area.value ? area.value.trim() + ' ' : '') + textChunk.trim();
            }
          }
        };

        speechRecognition.onerror = (e) => {
          console.error(e);
          isRecording = false;
          btn.classList.remove('btn-mic-active');
          label.textContent = "Start Dictation (Hindi/English)";
        };

        speechRecognition.start();
        isRecording = true;
        btn.classList.add('btn-mic-active');
        label.textContent = "Listening... Speak Hindi or English";
      }
    }'''

p_sr = c.find('function toggleSpeechRecording()')
if p_sr != -1:
    # Also strip devanagariToHinglish if present above
    p_dev = c.find('// Real-Time Devanagari to Hinglish')
    start_replace = p_dev if (p_dev != -1 and p_dev < p_sr) else p_sr
    p_end_sr = c.find('// Settings Modal', p_sr)
    c = c[:start_replace] + speech_func + '\n\n    ' + c[p_end_sr:]
    print('Restored native Google Live Speech Recognition')

# 3. Embed the new ClinicalAIEngine and re-engineer runExtraction
engine_code = '''    // ==========================================
    // REBUILT CLINICAL AI ENGINE (FROM SCRATCH)
    // Fast, Compact Line Protocol, Zero JSON Fragility
    // ==========================================
    class ClinicalAIEngine {
      constructor(apiKey = '') {
        this.apiKey = apiKey || (localStorage.getItem('GEMINI_API_KEY') || '').trim();
        this.primaryModel = 'gemini-1.5-flash';
        this.fallbackModels = ['gemini-1.5-flash-8b', 'gemini-2.0-flash', 'gemini-2.0-flash-lite'];
      }

      buildPrompt(clinicalText) {
        return `You are an expert Classical Homeopath and Repertory analyst.
Extract symptoms from this clinical consultation into 4 Kentian categories:
MIND, GENERALS, MODALITIES, PARTICULARS.

Consultation Text:
"""${clinicalText}"""

Output format strictly one symptom per line using this format:
[CATEGORY] Patient Symptom Description in Hinglish or English | SYNTHESIS_RUBRIC_KEYWORDS

Example format:
[MIND] raat ko akele me darr lagta hai | MIND FEAR ALONE DARK
[GENERALS] pyas bohot kam lagti hai, thand zyada | STOMACH THIRSTLESS CHILL
[MODALITIES] subah uthne par sab takleef badhti hai < morning | GENERALS MORNING WAKING AGG
[PARTICULARS] sar me daayein taraf tez dard | HEAD PAIN RIGHT

Output ONLY lines starting with [MIND], [GENERALS], [MODALITIES], or [PARTICULARS]. No conversational intro or markdown codeblocks.`;
      }

      async callGemini(model, prompt) {
        if (!this.apiKey) return null;
        const endpoint = `https://generativelanguage.googleapis.com/v1beta/models/${model}:generateContent?key=${this.apiKey}`;
        const payload = {
          contents: [{ parts: [{ text: prompt }] }],
          generationConfig: {
            temperature: 0.1,
            maxOutputTokens: 1200
          }
        };

        const res = await fetch(endpoint, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });

        if (res.ok) {
          const data = await res.json();
          return data.candidates?.[0]?.content?.parts?.[0]?.text || null;
        } else {
          const err = await res.json().catch(() => ({}));
          if (res.status === 429 || res.status === 403) {
            throw new Error(err.error?.message || 'Quota exceeded');
          }
          return null;
        }
      }

      parseClinicalResponse(rawText) {
        if (!rawText) return [];
        const lines = rawText.split('\\n');
        const symptoms = [];

        for (let rawLine of lines) {
          let line = rawLine.trim();
          if (!line) continue;

          const tagMatch = line.match(/^\\[(MIND|GENERALS|MODALITIES|PARTICULARS)\\]\\s*(.*?)(?:\\s*\\|\\s*(.*))?$/i);
          if (tagMatch) {
            const catTag = tagMatch[1].toUpperCase();
            let catName = 'Particulars & Locations';
            if (catTag === 'MIND') catName = 'Mind & Emotion';
            else if (catTag === 'GENERALS') catName = 'Physical Generals';
            else if (catTag === 'MODALITIES') catName = 'Modalities (< / >)';

            const symptomText = tagMatch[2].trim();
            const keywords = tagMatch[3] ? tagMatch[3].trim() : symptomText;

            if (symptomText.length > 2) {
              symptoms.push({
                category: catName,
                name: symptomText,
                weight: 2,
                synthesis_query: keywords
              });
            }
            continue;
          }

          line = line.replace(/^[-*•\\d\\.\\)]+\\s*/, '').trim();
          if (line.length > 3 && !/^(here is|here are|clinical symptoms|symptoms:)/i.test(line)) {
            let cat = 'Particulars & Locations';
            if (/mind|dar|ghabrahat|fear|anxiety|bechaini|restless/i.test(line)) cat = 'Mind & Emotion';
            else if (/general|thand|pyas|weakness|kamzori|sleep|neend|thakan/i.test(line)) cat = 'Physical Generals';
            else if (/modality|agg|amel|subah|raat|better|worse/i.test(line)) cat = 'Modalities (< / >)';

            symptoms.push({
              category: cat,
              name: line,
              weight: 2,
              synthesis_query: line
            });
          }
        }
        return symptoms;
      }

      offlineNLPFallback(text) {
        const symptoms = [];
        const lower = text.toLowerCase();

        const patterns = [
          { terms: ['sar dard', 'headache', 'sir dard', 'head pain', 'dard'], cat: 'Particulars & Locations', name: 'Headache / Pain', query: 'HEAD PAIN' },
          { terms: ['jalan', 'burning', 'acid', 'gastric', 'pet me jalan', 'stomach'], cat: 'Particulars & Locations', name: 'Gastric Burning / Stomach', query: 'STOMACH PAIN BURNING' },
          { terms: ['bechaini', 'restless', 'restlessness', 'tossing'], cat: 'Mind & Emotion', name: 'Restlessness / Anxiety', query: 'MIND RESTLESSNESS' },
          { terms: ['darr', 'dar', 'fear', 'dark', 'andhere', 'alone', 'akele'], cat: 'Mind & Emotion', name: 'Fear of Dark / Being Alone', query: 'MIND FEAR DARK' },
          { terms: ['thand', 'chill', 'chilly', 'cold sensitive'], cat: 'Physical Generals', name: 'Chilly / Sensitive to Cold', query: 'GENERALS COLD' },
          { terms: ['pyas', 'thirst', 'water', 'thirstless', 'pani'], cat: 'Physical Generals', name: 'Thirst Peculiarity', query: 'STOMACH THIRST' },
          { terms: ['neend', 'sleep', 'subah uthne', 'weakness', 'kamzori', 'thakan', 'tired'], cat: 'Physical Generals', name: 'Weakness / Fatigue on Waking', query: 'GENERALS WEAKNESS MORNING' },
          { terms: ['raat', 'midnight', 'night', '12 baje', 'after midnight'], cat: 'Modalities (< / >)', name: 'Worse at Night / Midnight (< night)', query: 'GENERALS NIGHT AGG' },
          { terms: ['subah', 'morning', 'waking'], cat: 'Modalities (< / >)', name: 'Worse in Morning on Waking (< morning)', query: 'GENERALS MORNING WAKING' }
        ];

        patterns.forEach(p => {
          for (let t of p.terms) {
            if (lower.includes(t)) {
              symptoms.push({
                category: p.cat,
                name: p.name,
                weight: 2,
                synthesis_query: p.query
              });
              break;
            }
          }
        });

        if (symptoms.length === 0) {
          symptoms.push({
            category: 'Particulars & Locations',
            name: text.substring(0, 50),
            weight: 2,
            synthesis_query: 'GENERALS WEAKNESS'
          });
        }
        return symptoms;
      }

      async extractSymptoms(text) {
        if (!text || !text.trim()) return { symptoms: [], modelUsed: 'None' };
        let rawOutput = null;
        let modelUsed = null;

        if (this.apiKey) {
          const prompt = this.buildPrompt(text);
          try {
            rawOutput = await this.callGemini(this.primaryModel, prompt);
            if (rawOutput) modelUsed = 'Gemini 1.5 Flash';
          } catch(e) {
            for (let fb of this.fallbackModels) {
              try {
                rawOutput = await this.callGemini(fb, prompt);
                if (rawOutput) {
                  modelUsed = `Gemini (${fb})`;
                  break;
                }
              } catch(err) {}
            }
          }
        }

        let symptoms = [];
        if (rawOutput) {
          symptoms = this.parseClinicalResponse(rawOutput);
        }

        if (!symptoms || symptoms.length === 0) {
          symptoms = this.offlineNLPFallback(text);
          modelUsed = this.apiKey ? 'In-Browser Clinical NLP' : 'In-Browser NLP (Add API Key for Flash)';
        }

        return { symptoms, modelUsed };
      }
    }
'''

# 4. Completely replace runExtraction with clean, streamlined async function
run_extraction_code = '''    // Step 1: Clean High-Precision AI Symptom Extraction
    async function runExtraction() {
      const text = document.getElementById('consultationText').value;
      if (!text.trim()) {
        alert("Please enter or dictate consultation text first.");
        return;
      }

      const apiKey = (localStorage.getItem('GEMINI_API_KEY') || '').trim();
      const extractBtn = document.getElementById('aiExtractBtn');
      const originalBtnHtml = extractBtn ? extractBtn.innerHTML : '';

      if (extractBtn) {
        extractBtn.disabled = true;
        extractBtn.innerHTML = `
          <i class="fa-solid fa-spinner fa-spin" style="color: #2563eb;"></i>
          <span>Extracting Symptoms...</span>
        `;
      }
      const autopilotBadge = document.getElementById('autopilotBadge');
      if (autopilotBadge) {
        autopilotBadge.innerHTML = `<i class="fa-solid fa-brain fa-pulse"></i> Resolving Synthesis Rubrics...`;
        autopilotBadge.style.background = '#eff6ff';
        autopilotBadge.style.color = '#1d4ed8';
      }

      try {
        const engine = new ClinicalAIEngine(apiKey);
        const result = await engine.extractSymptoms(text);

        // Resolve candidate rubrics from in-browser wasmDb with high accuracy
        result.symptoms.forEach(s => {
          s.candidate_rubrics = resolveCandidateRubricsFromDb(wasmDb, s);
        });

        // Update badge with active model status
        if (autopilotBadge) {
          autopilotBadge.textContent = `AI: ${result.modelUsed}`;
          autopilotBadge.style.background = '#dcfce7';
          autopilotBadge.style.color = '#166534';
        }

        // Clear current buckets
        document.getElementById('bucket-mind').innerHTML = '';
        document.getElementById('bucket-generals').innerHTML = '';
        document.getElementById('bucket-modalities').innerHTML = '';
        document.getElementById('bucket-particulars').innerHTML = '';

        // Render each extracted symptom
        result.symptoms.forEach((s, idx) => {
          renderSymptomCard(s, idx);
        });

        // Trigger repertorisation
        recalculateAndRender();

      } catch (err) {
        console.error("Extraction error:", err);
      } finally {
        if (extractBtn) {
          extractBtn.disabled = false;
          extractBtn.innerHTML = originalBtnHtml;
        }
      }
    }
'''

# Find runExtraction in index.html and replace old prompt/JSON/tryGenerate mess
pos_re = c.find('async function runExtraction()')
if pos_re != -1:
    pos_end_re = c.find('function renderSymptomCard(s, idx)', pos_re)
    if pos_end_re != -1:
        c = c[:pos_re] + engine_code + '\n\n' + run_extraction_code + '\n\n    ' + c[pos_end_re:]
        print('Successfully replaced old runExtraction with clean ClinicalAIEngine')

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(c)

print('Updated index.html successfully')
