import sqlite3
import re

conn = sqlite3.connect('synthesis.db')
c = conn.cursor()

def test_query_expansion(words):
    print(f"\n====================\nSearching combinations for: {words}")
    
    # 1. Try ALL words together with AND
    and_q = " AND ".join([f'"{w}"*' for w in words])
    sql_and = """
    SELECT f.symptom_id, f.path, s.level, COUNT(sr.remedy_abbreviation) as rem_count
    FROM syntree_fts( ? ) f
    JOIN syntree s ON f.symptom_id = s.id
    LEFT JOIN symptom_remedies sr ON s.id = sr.symptom_id
    GROUP BY f.symptom_id
    HAVING rem_count >= 1
    ORDER BY (s.level <= 3) DESC, rem_count DESC
    LIMIT 6
    """
    c.execute(sql_and, (and_q,))
    and_rows = c.fetchall()
    
    if and_rows:
        print(f"  [Found {len(and_rows)} exact AND matches]")
        for r in and_rows:
            print(f"    [{r[2]}] {r[1]} ({r[3]} rems)")
        return
        
    # 2. If no AND match with all words, try pairs or subsets
    print("  [No all-word match, trying subset combinations...]")
    for i in range(len(words)-1, 1, -1):
        import itertools
        for combo in itertools.combinations(words, i):
            sub_q = " AND ".join([f'"{w}"*' for w in combo])
            c.execute(sql_and, (sub_q,))
            sub_rows = c.fetchall()
            if sub_rows:
                print(f"  [Combo {' + '.join(combo)}: {len(sub_rows)} matches]")
                for r in sub_rows[:3]:
                    print(f"    [{r[2]}] {r[1]} ({r[3]} rems)")
                return

test_query_expansion(["HEAD", "PAIN", "VOMITING"])
test_query_expansion(["MIND", "FEAR", "DEATH"])
test_query_expansion(["RECTUM", "DIARRHEA", "CRAMPING"])
test_query_expansion(["STOMACH", "PAIN", "BURNING"])
test_query_expansion(["MIND", "RESTLESSNESS", "NIGHT"])
test_query_expansion(["STOMACH", "APPETITE", "WANTING"])
