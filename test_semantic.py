import sqlite3
import re

conn = sqlite3.connect('synthesis.db')
c = conn.cursor()

SYNONYMS = {
    "headache": ["HEAD", "PAIN"],
    "migraine": ["HEAD", "PAIN", "HEMICRANIA"],
    "vomiting": ["STOMACH", "VOMITING"],
    "nausea": ["STOMACH", "NAUSEA"],
    "diarrhea": ["RECTUM", "DIARRHEA", "STOOL"],
    "loose motion": ["RECTUM", "DIARRHEA"],
    "fever": ["FEVER"],
    "cough": ["COUGH"],
    "cold": ["NOSE", "CORYZA"],
    "runny nose": ["NOSE", "CORYZA"],
    "anorexia": ["STOMACH", "APPETITE", "WANTING"],
    "weakness": ["GENERALS", "WEAKNESS", "DEBILITY"],
    "fatigue": ["GENERALS", "WEAKNESS", "TIRED"],
    "tired": ["GENERALS", "WEAKNESS", "TIRED"],
    "thirst": ["STOMACH", "THIRST"],
    "sleeplessness": ["SLEEP", "SLEEPLESSNESS"],
    "insomnia": ["SLEEP", "SLEEPLESSNESS"],
    "restlessness": ["MIND", "RESTLESSNESS"],
    "anxiety": ["MIND", "ANXIETY"],
    "fear": ["MIND", "FEAR"],
    "anger": ["MIND", "ANGER", "IRRITABILITY"],
    "vertigo": ["VERTIGO"],
    "dizziness": ["VERTIGO"],
    "burning": ["BURNING", "PAIN"],
    "cramp": ["CRAMP", "PAIN"],
    "acidity": ["STOMACH", "ACIDITY", "ERUCTATIONS"],
    "gas": ["ABDOMEN", "DISTENSION", "FLATULENCE"],
    "constipation": ["RECTUM", "CONSTIPATION"],
    "piles": ["RECTUM", "HEMORRHOIDS"],
    "hemorrhoids": ["RECTUM", "HEMORRHOIDS"],
    "itching": ["SKIN", "ITCHING"],
    "eruption": ["SKIN", "ERUPTIONS"],
    "sweat": ["PERSPIRATION"],
    "perspiration": ["PERSPIRATION"]
}

def semantic_search(query, limit=15):
    q_lower = query.lower().strip()
    tokens = [t for t in re.split(r'[\s,\-_/]+', q_lower) if t]
    
    # Expand synonyms
    expanded_tokens = list(tokens)
    for t in tokens:
        if t in SYNONYMS:
            expanded_tokens.extend(SYNONYMS[t])
    for phrase, syns in SYNONYMS.items():
        if phrase in q_lower and phrase not in tokens:
            expanded_tokens.extend(syns)
            
    # Form FTS query with OR and NEAR
    fts_terms = []
    for term in set(expanded_tokens):
        cleaned = re.sub(r'[^a-zA-Z0-9]', '', term)
        if len(cleaned) >= 2:
            fts_terms.append(f'"{cleaned}"*')
            
    if not fts_terms:
        return []
        
    fts_query = " OR ".join(fts_terms)
    
    sql = """
    SELECT f.symptom_id, f.path, s.level, COUNT(sr.remedy_abbreviation) as rem_count, f.rank,
           cr.symptom_id as xref_target_id, cr.text as xref_target_path
    FROM syntree_fts( ? ) f
    JOIN syntree s ON f.symptom_id = s.id
    LEFT JOIN symptom_remedies sr ON s.id = sr.symptom_id
    LEFT JOIN cross_references cr ON s.id = cr.id
    GROUP BY f.symptom_id
    HAVING rem_count >= 1 OR cr.symptom_id IS NOT NULL
    ORDER BY (s.level <= 3) DESC, rem_count DESC, f.rank ASC
    LIMIT ?
    """
    c.execute(sql, (fts_query, limit * 2))
    rows = c.fetchall()
    
    print(f"\nResults for '{query}' (FTS: {fts_query[:50]}...):")
    for r in rows[:limit]:
        print(f"  {r[1]} (Level {r[2]}, {r[3]} rems)")

semantic_search("loose motion and stomach ache")
semantic_search("severe migraine with vomiting")
semantic_search("fear of dark and death")
semantic_search("acidity and gas after eating")
