import sqlite3
import time

def setup_fts():
    conn = sqlite3.connect('synthesis.db')
    c = conn.cursor()
    print("Checking syntree_fts...")
    c.execute("SELECT count(*) FROM sqlite_master WHERE type='table' AND name='syntree_fts'")
    exists = c.fetchone()[0]
    
    if not exists:
        print("Creating syntree_fts table...")
        c.execute("CREATE VIRTUAL TABLE syntree_fts USING fts5(symptom_id UNINDEXED, path, search_path)")
        print("Populating syntree_fts from syntree (180,386 rubrics)...")
        start = time.time()
        c.execute("INSERT INTO syntree_fts(symptom_id, path, search_path) SELECT id, path, search_path FROM syntree")
        conn.commit()
        print(f"Done in {time.time() - start:.2f}s! Total rows inserted:", c.rowcount)
    else:
        c.execute("SELECT count(*) FROM syntree_fts")
        print("syntree_fts already exists with row count:", c.fetchone()[0])

if __name__ == '__main__':
    setup_fts()
