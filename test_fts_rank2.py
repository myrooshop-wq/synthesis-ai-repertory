import sqlite3
import re

conn = sqlite3.connect('synthesis.db')
c = conn.cursor()

def test_or_ranking(query_words):
    # Test OR match where we count how many distinct query words matched!
    or_terms = ' OR '.join([f'"{w.upper()}"' for w in query_words])
    print(f"\n--- Testing OR ranking for: {query_words} ---")
    
    sql = f"""
    SELECT f.symptom_id, f.path, s.level, COUNT(sr.remedy_abbreviation) as rem_count, f.rank
    FROM syntree_fts( ? ) f
    JOIN syntree s ON f.symptom_id = s.id
    LEFT JOIN symptom_remedies sr ON s.id = sr.symptom_id
    GROUP BY f.symptom_id
    HAVING rem_count >= 1
    LIMIT 200
    """
    c.execute(sql, (or_terms,))
    rows = c.fetchall()
    
    scored = []
    for r in rows:
        path_up = r[1].upper()
        # Count matched query concepts
        hits = sum(1 for w in query_words if w.upper() in path_up)
        # Score prioritizing hits, then level <= 3, then remedy_count
        score = (hits * 1000) + (100 if r[2] <= 3 else 0) + min(r[3], 500)
        scored.append((score, hits, r[2], r[3], r[1]))
        
    scored.sort(key=lambda x: -x[0])
    for s in scored[:6]:
        print(f"  Score {s[0]} | Hits: {s[1]}/{len(query_words)} | Level {s[2]} | {s[3]} rems | {s[4]}")

test_or_ranking(["HEAD", "PAIN", "VOMITING"])
test_or_ranking(["MIND", "FEAR", "DARK", "DEATH"])
test_or_ranking(["STOMACH", "BURNING", "EATING"])
test_or_ranking(["RECTUM", "DIARRHEA", "CRAMPING"])
