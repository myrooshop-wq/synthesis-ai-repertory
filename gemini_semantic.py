import json
import urllib.request
import urllib.error

def query_gemini_semantic(api_key, query):
    prompt = f"""
You are a master Homeopath and Synthesis Repertory Scholar.
A doctor is searching the Synthesis Repertory with this clinical query:
"{query}"

Map this clinical condition to the top 3-5 best classical Kentian/Synthesis rubrics in standard uppercase format:
Examples:
- "headache after eating": ["HEAD - PAIN - eating - after - agg.", "HEAD - PAIN", "STOMACH - PAIN"]
- "migraine right side": ["HEAD - PAIN - Sides - right", "HEAD - PAIN - Sides - one side", "HEAD - PAIN"]
- "loose motion": ["RECTUM - DIARRHEA", "STOOL - THIN", "ABDOMEN - PAIN - cramping"]
- "fear of dark": ["MIND - FEAR - dark; of", "MIND - FEAR", "MIND - ANXIETY - dark; in the"]

Return ONLY a valid JSON list of 3-5 rubric search strings:
["CHAPTER - RUBRIC", "CHAPTER - RUBRIC - SUBRUBRIC"]
"""
    payload = json.dumps({
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.1, "maxOutputTokens": 200}
    }).encode("utf-8")
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash-lite:generateContent?key={api_key}"
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            text = data["candidates"][0]["content"]["parts"][0]["text"]
            import re
            m = re.search(r'\[.*\]', text, re.DOTALL)
            if m:
                return json.loads(m.group(0))
    except Exception as e:
        print("Gemini call error:", e)
    return []

print("Helper ready")
