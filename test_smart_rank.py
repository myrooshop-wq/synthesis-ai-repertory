import sqlite3
import re

conn = sqlite3.connect('synthesis.db')
c = conn.cursor()

STOPWORDS = {"and", "or", "the", "a", "an", "in", "on", "at", "to", "for", "of", "with", "from", "by", "is", "after"}

SYNONYMS = {
    "headache": ["HEAD", "PAIN"],
    "migraine": ["HEAD", "PAIN", "HEMICRANIA"],
    "vomiting": ["STOMACH", "VOMITING"],
    "nausea": ["STOMACH", "NAUSEA"],
    "diarrhea": ["RECTUM", "DIARRHEA"],
    "loose": ["RECTUM", "DIARRHEA"],
    "fever": ["FEVER"],
    "cough": ["COUGH"],
    "cold": ["NOSE", "CORYZA"],
    "coryza": ["NOSE", "CORYZA"],
    "anorexia": ["STOMACH", "APPETITE", "WANTING"],
    "weakness": ["GENERALS", "WEAKNESS"],
    "fatigue": ["GENERALS", "WEAKNESS"],
    "tired": ["GENERALS", "WEAKNESS", "TIRED"],
    "thirst": ["STOMACH", "THIRST"],
    "sleeplessness": ["SLEEP", "SLEEPLESSNESS"],
    "insomnia": ["SLEEP", "SLEEPLESSNESS"],
    "restlessness": ["MIND", "RESTLESSNESS"],
    "anxiety": ["MIND", "ANXIETY"],
    "fear": ["MIND", "FEAR"],
    "dark": ["DARK"],
    "death": ["DEATH"],
    "anger": ["MIND", "ANGER"],
    "irritability": ["MIND", "IRRITABILITY"],
    "vertigo": ["VERTIGO"],
    "dizziness": ["VERTIGO"],
    "burning": ["BURNING"],
    "cramp": ["CRAMPING", "PAIN"],
    "acidity": ["STOMACH", "ERUCTATIONS", "ACIDITY"],
    "gas": ["ABDOMEN", "DISTENSION", "FLATULENCE"],
    "constipation": ["RECTUM", "CONSTIPATION"],
    "piles": ["RECTUM", "HEMORRHOIDS"],
    "itching": ["SKIN", "ITCHING"],
    "sweat": ["PERSPIRATION"],
    "perspiration": ["PERSPIRATION"]
}

def rank_test(query):
    print(f"\n====================\nQuery: '{query}'")
    q_lower = query.lower()
    raw_tokens = [t for t in re.split(r'[^a-zA-Z0-9]+', q_lower) if t and t not in STOPWORDS]
    
    # Identify key concept groups
    concept_terms = set(raw_tokens)
    for t in raw_tokens:
        if t in SYNONYMS:
            concept_terms.update(SYNONYMS[t])
    for p, syns in SYNONYMS.items():
        if p in q_lower:
            concept_terms.update(syns)
            
    # For FTS, build query
    fts_tokens = [f'"{term.upper()}"*' for term in concept_terms if len(term) >= 3]
    if not fts_tokens:
        return
        
    fts_q = " OR ".join(fts_tokens)
    sql = """
    SELECT f.symptom_id, f.path, s.level, COUNT(sr.remedy_abbreviation) as rem_count, f.rank
    FROM syntree_fts( ? ) f
    JOIN syntree s ON f.symptom_id = s.id
    LEFT JOIN symptom_remedies sr ON s.id = sr.symptom_id
    GROUP BY f.symptom_id
    LIMIT 300
    """
    c.execute(sql, (fts_q,))
    rows = c.fetchall()
    
    # Python-side semantic scoring: count how many query concept words appear in path!
    scored = []
    for r in rows:
        path_upper = r[1].upper()
        # How many query concepts match?
        matches = sum(1 for term in concept_terms if term.upper() in path_upper)
        if matches == 0:
            continue
        # Score = matches * 100 + (30 if level<=3 else 0) + min(rem_count, 500)/10.0 - rank
        score = (matches * 100.0) + (40.0 if r[2] <= 3 else 0.0) + (min(r[3], 300) / 10.0) - float(r[4])
        scored.append((score, matches, r[0], r[1], r[2], r[3]))
        
    scored.sort(key=lambda x: -x[0])
    for s in scored[:6]:
        print(f"  Score: {s[0]:.1f} (Matches {s[1]}, Rems {s[5]}) -> {s[3]}")

rank_test("severe migraine with vomiting")
rank_test("loose motion diarrhea with abdominal cramps")
rank_test("fear of dark and death")
rank_test("acidity burning stomach after eating")
