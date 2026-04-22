import sqlite3
import os

db_path = os.path.join('data', 'museum.db')
if not os.path.exists(db_path):
    print(f"Database not found at {db_path}")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Add Salar Jung Museum if it doesn't exist
cursor.execute("SELECT id FROM exhibitions WHERE title LIKE '%Salar Jung%'")
if not cursor.fetchone():
    print("Adding Salar Jung Museum to database...")
    cursor.execute("""
        INSERT INTO exhibitions (title, description, price, availability_status, opening_time, closing_time)
        VALUES (?, ?, ?, ?, ?, ?)
    """, ("Salar Jung Museum, Hyderabad", "One of the three National Museums of India, housing a vast collection of art and artifacts.", 100, "Open", "10:00", "17:00"))
    conn.commit()
    print("Salar Jung Museum added successfully.")
else:
    print("Salar Jung Museum already exists.")

conn.close()
