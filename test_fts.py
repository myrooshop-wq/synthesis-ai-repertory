import sqlite3

conn = sqlite3.connect('synthesis.db')
c = conn.cursor()

def test_search(query):
    print(f"\n--- Searching for: '{query}' ---")
    sql = """
    SELECT f.symptom_id, f.path, s.level, COUNT(sr.remedy_abbreviation) as rem_count, f.rank
    FROM syntree_fts( ? ) f
    JOIN syntree s ON f.symptom_id = s.id
    LEFT JOIN symptom_remedies sr ON s.id = sr.symptom_id
    GROUP BY f.symptom_id
    ORDER BY (s.level <= 3) DESC, rem_count DESC, f.rank ASC
    LIMIT 5
    """
    c.execute(sql, (query,))
    for row in c.fetchall():
        print(f"ID: {row[0]} | Level: {row[2]} | Rems: {row[3]} | Rank: {row[4]:.2f} | Path: {row[1]}")

test_search("headache")
test_search("migraine")
test_search("restless night")
test_search("burning stomach")
