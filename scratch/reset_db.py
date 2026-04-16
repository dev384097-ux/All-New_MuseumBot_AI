import sqlite3
import os

DB_PATH = os.path.join('data', 'museum.db')
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

# Clear existing data and reset IDs
c.execute('DELETE FROM exhibitions')
c.execute("DELETE FROM sqlite_sequence WHERE name='exhibitions'")

# Insert official museum sites
exhibitions = [
    ('National Science Centre, New Delhi', 'Premier science museum in the capital with interactive galleries.', 100.0),
    ('Nehru Science Centre, Mumbai', 'India\'s largest interactive science center located in Worli.', 100.0),
    ('BITM Kolkata', 'The first science museum in India, focusing on industrial and technological heritage.', 100.0),
    ('Science City, Ahmedabad', 'A large-scale science center featuring an IMAX theater and pavilion.', 100.0)
]
c.executemany('INSERT INTO exhibitions (title, description, price) VALUES (?, ?, ?)', exhibitions)

conn.commit()
conn.close()
print('Database updated and IDs reset successfully.')
