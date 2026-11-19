import os
import sqlite3

con = sqlite3.connect('synthesis.db')
cur = con.cursor()
cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cur.fetchall()
print("Tables in synthesis.db:")
for t in tables:
    name = t[0]
    try:
        cur.execute(f'SELECT count(*) FROM "{name}"')
        print(f"  {name}: {cur.fetchone()[0]:,} rows")
    except Exception as e:
        print(f"  {name}: {e}")

cur.execute("SELECT name, sql FROM sqlite_master WHERE type='index'")
indexes = cur.fetchall()
print("\nIndexes in synthesis.db:")
for name, sql in indexes:
    print(f"  {name}")
con.close()
