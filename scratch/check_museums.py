import sqlite3
import os

db_path = os.path.join('data', 'museum.db')
if not os.path.exists(db_path):
    print(f"Database not found at {db_path}")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("EXHIBITIONS IN DATABASE:")
cursor.execute("SELECT id, title FROM exhibitions")
for row in cursor.fetchall():
    print(f"ID: {row[0]} | Title: {row[1]}")

conn.close()
