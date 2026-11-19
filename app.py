import os
import json
import sqlite3
import urllib.request
import urllib.error
from typing import Optional, List, Dict, Any
from flask import Flask, request, jsonify, send_file
from repertory_engine import RepertoryServer

app = Flask(__name__, static_folder="static")
engine = RepertoryServer("synthesis.db")

# Fallback sequence of Gemini models as specified by user
GEMINI_MODELS = [
    "gemini-2.0-flash",           # or gemini-1.5-flash / gemini-2.0-flash-exp
    "gemini-1.5-flash-8b",        # flash-lite tier
    "gemini-1.5-pro",             # pro tier
    "gemini-1.5-flash"
]

def get_available_gemini_models(api_key: str):
    """Dynamically query Google Gemini API to get the exact models active for this key."""
    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
    req = urllib.request.Request(url)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            models = [m["name"].replace("models/", "") for m in data.get("models", []) if "generateContent" in m.get("supportedGenerationMethods", [])]
            print(f"[Gemini] Discovered {len(models)} active models for key:", models[:8])
            return models
    except Exception as e:
        print("[Gemini] Failed to list models dynamically:", e)
        return []

def call_gemini_with_fallback(api_key: str, prompt: str):
    """Dynamically queries available models, or tries the exact latest Gemini generation."""
    discovered = get_available_gemini_models(api_key)
    
    # Exactly what Google demanded in the error message:
    preferred = [
        "gemini-3.8-flash",
        "gemini-3.5-flash-lite",
        "gemini-3.1-pro-preview",
        "gemini-3.1-flash-lite",
        "gemini-flash-latest",
        "gemini-flash-lite-latest",
        "gemini-pro-latest"
    ]
    
    # Combine user's preferred with discovered
    models_to_try = [m for m in preferred if m in discovered] if discovered else []
    if not models_to_try:
        # Filter out discontinued 2.5 and 1.5 versions
        models_to_try = [m for m in discovered if not m.startswith("gemini-2.5") and not m.startswith("gemini-1.5") and not "tts" in m]
    if not models_to_try:
        models_to_try = preferred

    print("[Gemini] Models to try in sequence:", models_to_try[:5])
    
    last_error = None
    for model in models_to_try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }],
            "generationConfig": {
                "temperature": 0.2
            }
        }
        req = urllib.request.Request(
            url,
            headers={"Content-Type": "application/json"},
            data=json.dumps(payload).encode("utf-8")
        )
        try:
            print(f"[Gemini] Trying active model: {model}...")
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                text = data["candidates"][0]["content"]["parts"][0]["text"]
                print(f"[Gemini] SUCCESS with model: {model}!")
                return text, model
        except urllib.error.HTTPError as e:
            err_body = e.read().decode('utf-8', errors='ignore')
            print(f"[Gemini] Error on {model}: {e.code} - {err_body}")
            last_error = f"{e.code}: {err_body}"
            continue
        except Exception as e:
            print(f"[Gemini] Exception on {model}: {e}")
            last_error = str(e)
            continue
            
    return None, last_error

@app.route("/")
def index():
    return send_file("static/index.html")

@app.route("/api/autocomplete", methods=["GET"])
def autocomplete():
    q = request.args.get("q", "")
    limit = int(request.args.get("limit", 15))
    is_semantic = request.args.get("semantic", "false").lower() in ("true", "1")
    
    if is_semantic:
        results = engine.semantic_rubric_search(q, limit)
    else:
        results = engine.autocomplete_rubrics(q, limit)
    return jsonify(results)

@app.route("/api/rubric-children", methods=["GET"])
def rubric_children():
    """
    Returns immediate child sub-rubrics under a given parent rubric:
    e.g. Under 'MIND - ANXIETY' returns:
      - 'daytime'
      - 'morning'
      - 'abdomen; with complaints of'
      - 'Bladder; with pain in'
    """
    parent_id = int(request.args.get("parent_id", 0))
    c = engine.conn.cursor()
    c.execute("""
    SELECT s.id, s.item, s.path, s.level, COUNT(sr.remedy_abbreviation) as remedy_count
    FROM syntree s
    LEFT JOIN symptom_remedies sr ON s.id = sr.symptom_id
    WHERE s.id_father = ?
    GROUP BY s.id
    ORDER BY s.order_index ASC, s.item ASC
    LIMIT 60
    """, (parent_id,))
    rows = c.fetchall()
    return jsonify([dict(r) for r in rows])

@app.route("/api/rubric-book-view", methods=["GET"])
def rubric_book_view():
    """
    Renders the exact Synthesis Book Page view for a rubric:
    - Full breadcrumb hierarchy (Chapters -> Parent -> Current)
    - Full list of remedies formatted in Synthesis typography:
        * Grade 4: Bold Red / CAPS
        * Grade 3: Bold Red
        * Grade 2: Blue Italics
        * Grade 1: Plain Roman
    - Author footnote citation superscripts
    - Cross references (<Xrf>)
    - Sub-rubric branches WITH exact remedy counts (e.g. "+ morning (213)")
    """
    sid = int(request.args.get("symptom_id", 0))
    highlight_remedy = request.args.get("remedy", "").lower().strip()
    c = engine.conn.cursor()

    # Rubric details
    c.execute("SELECT * FROM syntree WHERE id = ?", (sid,))
    rubric = c.fetchone()
    if not rubric:
        return jsonify({"error": "Rubric not found"}), 404

    # Build ancestor breadcrumbs (e.g. Chapters -> GENERALS -> WEAKNESS -> right side)
    breadcrumbs = []
    curr_id = rubric["id_father"]
    while curr_id:
        c.execute("SELECT id, id_father, item, path FROM syntree WHERE id = ?", (curr_id,))
        p = c.fetchone()
        if not p:
            break
        breadcrumbs.insert(0, dict(p))
        curr_id = p["id_father"]

    # Remedies with degrees and author abbreviations
    c.execute("""
    SELECT 
        sr.remedy_abbreviation, 
        sr.degree, 
        sr.text, 
        r.description as remedy_full,
        GROUP_CONCAT(ra.author_abbreviation, ', ') as authors
    FROM symptom_remedies sr
    LEFT JOIN remedies r ON sr.remedy_abbreviation = r.remedy_abbreviation
    LEFT JOIN remedy_authors ra ON sr.symptom_id = ra.symptom_id AND sr.remedy_abbreviation = ra.remedy_abbreviation
    WHERE sr.symptom_id = ?
    GROUP BY sr.remedy_abbreviation
    ORDER BY sr.degree DESC, sr.remedy_abbreviation ASC
    """, (sid,))
    remedy_rows = [dict(r) for r in c.fetchall()]

    # Cross references (In Synthesis DB schema, id is the source symptom_id, text is the target rubric to compare!)
    c.execute("""
    SELECT DISTINCT symptom_id as target_symptom_id, text, kind 
    FROM cross_references 
    WHERE id = ?
    ORDER BY text ASC
    """, (sid,))
    xrefs = [dict(r) for r in c.fetchall()]

    # Child sub-rubrics WITH exact remedy count!
    c.execute("""
    SELECT s.id, s.item, s.path, s.level, COUNT(sr.remedy_abbreviation) as remedy_count
    FROM syntree s
    LEFT JOIN symptom_remedies sr ON s.id = sr.symptom_id
    WHERE s.id_father = ?
    GROUP BY s.id
    ORDER BY s.order_index ASC, s.item ASC
    LIMIT 60
    """, (sid,))
    children = [dict(r) for r in c.fetchall()]

    return jsonify({
        "rubric": dict(rubric),
        "breadcrumbs": breadcrumbs,
        "highlight_remedy": highlight_remedy,
        "remedies": remedy_rows,
        "cross_references": xrefs,
        "children": children
    })

@app.route("/api/chapters", methods=["GET"])
def get_chapters():
    """Returns top-level root chapters (Mind, Vertigo, Head, etc.)."""
    c = engine.conn.cursor()
    c.execute("""
    SELECT id, item, path 
    FROM syntree 
    WHERE id_father IS NULL 
    ORDER BY order_index ASC
    """)
    rows = [dict(r) for r in c.fetchall()]
    return jsonify(rows)

@app.route("/api/cell-citation", methods=["GET"])
def cell_citation():
    sid = int(request.args.get("symptom_id", 0))
    remedy = request.args.get("remedy", "")
    data = engine.get_cell_citation(sid, remedy)
    return jsonify(data)

@app.route("/api/repertorise", methods=["POST"])
def repertorise():
    payload = request.json or {}
    weights_raw = payload.get("weights", {})
    weights = {int(k): int(v) for k, v in weights_raw.items()}
    eliminating_ids = [int(x) for x in payload.get("eliminating_ids", [])]
    min_degree = int(payload.get("min_degree", 1))
    top_n = int(payload.get("top_n", 12))
    is_acute_mode = bool(payload.get("is_acute_mode", False))

    matrix_res = engine.repertorise_matrix(
        symptom_weights=weights,
        eliminating_symptom_ids=eliminating_ids,
        min_degree=min_degree,
        top_n=top_n,
        is_acute_mode=is_acute_mode
    )
    return jsonify(matrix_res)

@app.route("/api/ai-extract-symptoms", methods=["POST"])
def ai_extract_symptoms():
    data = request.json or {}
    transcript = data.get("transcript", "")
    api_key = data.get("api_key", "").strip()

    if not transcript:
        return jsonify({"symptoms": []})

    # If Gemini API key is provided, use Generative LLM
    if api_key:
        print(f"[API] Received extraction request with key (starts with {api_key[:6]}...)")
        prompt = f"""
You are an expert Homeopathic Physician and Repertorizer. Analyze this patient narrative:
\"\"\"{transcript}\"\"\"

Task:
Extract the key symptoms into Kentian clinical categories:
1. "Mind & Emotion"
2. "Physical Generals" (chilly/hot thermals, thirst, appetite, sleep, sweat)
3. "Modalities (< / >)" (time of aggravation <, amelioration >)
4. "Particulars & Locations" (headache, body ache, fever, stomach)

CRITICAL RULE FOR "synthesis_query":
Always provide 2 to 3 standard, classical, broad repertory keywords found in Kent/Synthesis Repertory that have MANY remedies.
DO NOT use rare or obscure sub-rubrics. Use standard rubrics:
- For loss of appetite / anorexia: USE "STOMACH APPETITE WANTING" (NEVER use ravenous)
- For fever: USE "FEVER CONTINUED" or "FEVER HEAT"
- For headache with fever: USE "HEAD PAIN"
- For body ache / limb pains: USE "EXTREMITIES PAIN" or "GENERALS PAIN"
- For weakness: USE "GENERALS WEAKNESS"
- For restlessness at night: USE "MIND RESTLESSNESS NIGHT"
- For sleeplessness: USE "SLEEP SLEEPLESSNESS"
- For chill with fever: USE "CHILL FEVER"

Format Output as valid JSON strictly adhering to this structure:
{{
  "symptoms": [
     {{
       "category": "Mind & Emotion",
       "name": "Restlessness at night (रात में बेचैनी)",
       "weight": 2,
       "synthesis_query": "MIND RESTLESSNESS NIGHT"
     }}
  ]
}}
"""
        gemini_text, used_or_err = call_gemini_with_fallback(api_key, prompt)
        if gemini_text:
            try:
                # Strip any accidental ```json ... ``` wrapper
                clean_text = gemini_text.strip()
                if clean_text.startswith("```"):
                    lines = clean_text.split("\n")
                    clean_text = "\n".join(lines[1:-1] if lines[-1].startswith("```") else lines[1:])
                parsed = json.loads(clean_text)
                symptoms = parsed.get("symptoms", [])
                for s in symptoms:
                    q = s.get("synthesis_query", "")
                    s["candidate_rubrics"] = engine.autocomplete_rubrics(q, limit=3, require_remedies=True)
                print(f"[Gemini] Parsed {len(symptoms)} symptoms via {used_or_err}!")
                return jsonify({"symptoms": symptoms, "model_used": f"Gemini ({used_or_err})"})
            except Exception as parse_err:
                print("[Gemini] JSON Parse Error:", parse_err, "Raw text:", gemini_text[:200])
        else:
            print("[Gemini] API calls failed:", used_or_err)
    else:
        print("[API] No API key received in request payload.")

    # Fallback to Local Rule Engine if no API key or if API failed
    last_err_msg = used_or_err if api_key and not gemini_text else None
    symptom_dictionary = [
        {"triggers": ["restless", "bechain", "बेचैन", "bechaini"], "category": "Mind & Emotion", "name": "Restlessness (मानसिक/शारीरिक बेचैनी)", "synthesis_query": "MIND RESTLESSNESS", "weight": 2},
        {"triggers": ["fear of dark", "darkness", "andhere se dar", "अंधेरे से डर"], "category": "Mind & Emotion", "name": "Fear of darkness (अंधेरे का भय)", "synthesis_query": "MIND FEAR DARK", "weight": 2},
        {"triggers": ["anger", "irritable", "gussa", "गुस्सा", "chidchida"], "category": "Mind & Emotion", "name": "Irritability / Anger (गुस्सा / चिड़चिड़ापन)", "synthesis_query": "MIND IRRITABILITY", "weight": 1},
        {"triggers": ["anxiety", "ghabrahat", "घबराहट"], "category": "Mind & Emotion", "name": "Anxiety (घबराहट / चिंता)", "synthesis_query": "MIND ANXIETY", "weight": 2},
        {"triggers": ["chilly", "cold body", "thandi", "ठंड लगती है", "sardi"], "category": "Physical Generals", "name": "Chilly patient (अत्यधिक ठंड लगना)", "synthesis_query": "GENERALS COLD AIR AGG", "weight": 2},
        {"triggers": ["hot patient", "garmi", "गर्मी ज्यादा लगती है", "sweat"], "category": "Physical Generals", "name": "Warm / Hot patient (गर्मी लगना)", "synthesis_query": "GENERALS WARMTH AGG", "weight": 2},
        {"triggers": ["thirst small quantities", "thoda thoda pani", "घूंट घूंट पानी", "frequent sips"], "category": "Physical Generals", "name": "Thirst for small quantities often", "synthesis_query": "STOMACH THIRST SMALL QUANTITIES", "weight": 3},
        {"triggers": ["thirstless", "pyas nahi", "प्यास नहीं लगती"], "category": "Physical Generals", "name": "Thirstless (प्यास का अभाव)", "synthesis_query": "STOMACH THIRSTLESSNESS", "weight": 2},
        {"triggers": ["midnight", "aadhi raat", "रात 12", "रात 1"], "category": "Modalities (< / >)", "name": "Aggravation after midnight (<$ Midnight)", "synthesis_query": "GENERALS NIGHT MIDNIGHT AFTER", "weight": 2},
        {"triggers": ["warm drinks", "garam pani se aaram", "गरम पानी", "warm food"], "category": "Modalities (< / >)", "name": "Amelioration from warm drinks (>$ Warm drinks)", "synthesis_query": "GENERALS WARM DRINKS AMEL", "weight": 2},
        {"triggers": ["burning", "jalan", "जलन"], "category": "Particulars & Locations", "name": "Burning pain (जलनदार दर्द)", "synthesis_query": "STOMACH PAIN BURNING", "weight": 2},
        {"triggers": ["headache", "sar dard", "सिर दर्द"], "category": "Particulars & Locations", "name": "Headache (सिर दर्द)", "synthesis_query": "HEAD PAIN", "weight": 1},
        {"triggers": ["stomach pain", "pet dard", "पेट में दर्द"], "category": "Particulars & Locations", "name": "Gastric pain / Stomach ache", "synthesis_query": "STOMACH PAIN", "weight": 2},
        {"triggers": ["vomit", "ulti", "उल्टी"], "category": "Particulars & Locations", "name": "Nausea & Vomiting (उल्टी / मिचली)", "synthesis_query": "STOMACH VOMITING", "weight": 1}
    ]

    extracted = []
    seen = set()
    text_low = transcript.lower()
    for item in symptom_dictionary:
        for trig in item["triggers"]:
            if trig in text_low:
                if item["name"] not in seen:
                    seen.add(item["name"])
                    candidates = engine.autocomplete_rubrics(item["synthesis_query"], limit=3)
                    extracted.append({
                        "category": item["category"],
                        "name": item["name"],
                        "weight": item["weight"],
                        "synthesis_query": item["synthesis_query"],
                        "candidate_rubrics": candidates
                    })
                break

    return jsonify({
        "symptoms": extracted, 
        "model_used": "Local Rule-Engine (Offline)",
        "gemini_error": last_err_msg
    })

if __name__ == "__main__":
    # Listen on 0.0.0.0 so phone on same Wi-Fi can connect!
    app.run(host="0.0.0.0", port=5055, debug=False)
