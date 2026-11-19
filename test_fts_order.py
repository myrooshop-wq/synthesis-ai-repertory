import sqlite3
import re

conn = sqlite3.connect('synthesis.db')
c = conn.cursor()

def test_fts_order(query):
    print(f"\n--- FTS MATCH for: '{query}' ---")
    sql = """
    SELECT f.symptom_id, f.path, s.level, COUNT(sr.remedy_abbreviation) as rem_count, f.rank
    FROM syntree_fts( ? ) f
    JOIN syntree s ON f.symptom_id = s.id
    LEFT JOIN symptom_remedies sr ON s.id = sr.symptom_id
    GROUP BY f.symptom_id
    ORDER BY (s.level <= 3) DESC, rem_count DESC, f.rank ASC
    LIMIT 6
    """
    c.execute(sql, (query,))
    for r in c.fetchall():
        print(f"  [{r[2]}] {r[1]} ({r[3]} rems, rank: {r[4]:.2f})")

test_fts_order('"HEAD" AND "PAIN"')
test_fts_order('"HEAD" AND "PAIN" AND "VOMITING"')
test_fts_order('"RECTUM" AND "DIARRHEA"')
test_fts_order('"STOMACH" AND "BURNING"')
test_fts_order('"MIND" AND "FEAR" AND "DEATH"')
