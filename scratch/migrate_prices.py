import sqlite3
import os

DB_PATH = os.path.join('d:\\CAPSTONE', 'data', 'museum.db')

def migrate():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # 1. Add columns if they don't exist
    try:
        c.execute('ALTER TABLE exhibitions ADD COLUMN student_price REAL DEFAULT 1.0')
        print("Added student_price column.")
    except Exception as e:
        print(f"student_price already exists or error: {e}")
        
    try:
        c.execute('ALTER TABLE exhibitions ADD COLUMN group_price REAL DEFAULT 80.0')
        print("Added group_price column.")
    except Exception as e:
        print(f"group_price already exists or error: {e}")
        
    # 2. Update varied prices for existing museums
    updates = [
        (80.0, 1.0, 60.0, "BITM Kolkata"),
        (120.0, 20.0, 100.0, "Science City, Ahmedabad"),
        (150.0, 50.0, 120.0, "Salar Jung Museum, Hyderabad")
    ]
    
    for adult, student, group, title in updates:
        c.execute('UPDATE exhibitions SET price = ?, student_price = ?, group_price = ? WHERE title = ?', (adult, student, group, title))
    
    # 3. Ensure Salar Jung exists (it might not have been in the original seed)
    c.execute('SELECT * FROM exhibitions WHERE title = "Salar Jung Museum, Hyderabad"')
    if not c.fetchone():
        c.execute('INSERT INTO exhibitions (title, description, price, student_price, group_price, opening_time, closing_time, holidays) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                  ("Salar Jung Museum, Hyderabad", "Home to one of the largest private collections in the world.", 150.0, 50.0, 120.0, '10:00', '17:00', 'Every Friday'))
        print("Added Salar Jung Museum.")

    conn.commit()
    conn.close()
    print("Migration completed.")

if __name__ == '__main__':
    migrate()
