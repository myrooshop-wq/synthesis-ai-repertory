import sqlite3

conn = sqlite3.connect('d:/software by me/synthesis homeopathy/synthesis.db')
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
print('Tables in synthesis.db:', [r[0] for r in cursor.fetchall()])
