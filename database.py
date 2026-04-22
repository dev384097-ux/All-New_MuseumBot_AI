import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'data', 'museum.db')

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    
    # Create Users table
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            email TEXT UNIQUE,
            password_hash TEXT,
            otp TEXT,
            is_verified BOOLEAN DEFAULT 0,
            full_name TEXT
        )
    ''')

    # Create Exhibitions table
    c.execute('''
        CREATE TABLE IF NOT EXISTS exhibitions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            price REAL NOT NULL,
            student_price REAL DEFAULT 1.0,
            group_price REAL DEFAULT 80.0,
            availability_status TEXT DEFAULT 'Open',
            opening_time TEXT DEFAULT '09:30',
            closing_time TEXT DEFAULT '18:00',
            holidays TEXT DEFAULT 'Holi, Diwali'
        )
    ''')

    
    # Create Bookings table
    c.execute('''
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            visitor_name TEXT,
            visit_date TEXT,
            exhibition_id INTEGER,
            num_tickets INTEGER,
            total_price REAL,
            ticket_hash TEXT,
            status TEXT DEFAULT 'Pending Payment',
            razorpay_order_id TEXT,
            razorpay_payment_id TEXT,
            razorpay_signature TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id),
            FOREIGN KEY(exhibition_id) REFERENCES exhibitions(id)
        )
    ''')
    
    # Create Announcements table
    c.execute('''
        CREATE TABLE IF NOT EXISTS announcements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            museum_id INTEGER,
            title TEXT NOT NULL,
            description TEXT,
            date_published TEXT,
            redirect_url TEXT,
            is_active BOOLEAN DEFAULT 1,
            FOREIGN KEY(museum_id) REFERENCES exhibitions(id)
        )
    ''')

    
    # Insert some mock exhibitions
    c.execute('SELECT COUNT(*) FROM exhibitions')
    if c.fetchone()[0] == 0:
        exhibitions = [
            ("National Science Centre, New Delhi", "Premier science museum in the capital with interactive galleries.", 100.0, 1.0, 80.0, '09:30', '18:00', 'Holi & Diwali'),
            ("Nehru Science Centre, Mumbai", "India's largest interactive science center located in Worli.", 100.0, 1.0, 80.0, '09:30', '18:00', 'Holi & Diwali'),
            ("BITM Kolkata", "The first science museum in India, focusing on industrial and technological heritage.", 80.0, 1.0, 60.0, '09:30', '18:00', 'Holi & Diwali'),
            ("Science City, Ahmedabad", "A large-scale science center featuring an IMAX theater and pavilion.", 120.0, 20.0, 100.0, '10:00', '20:00', 'Every Monday'),
            ("Salar Jung Museum, Hyderabad", "Home to one of the largest private collections in the world.", 150.0, 50.0, 120.0, '10:00', '17:00', 'Every Friday')
        ]
        c.executemany('INSERT INTO exhibitions (title, description, price, student_price, group_price, opening_time, closing_time, holidays) VALUES (?, ?, ?, ?, ?, ?, ?, ?)', exhibitions)


    # Insert some dynamic mock announcements if empty
    c.execute('SELECT COUNT(*) FROM announcements')
    if c.fetchone()[0] == 0:
        from datetime import datetime, timedelta
        today = datetime.now()
        announcements = [
            (1, "Ancient Indian Astronomy", "Explore the celestial wisdom of our ancestors at NSC Delhi's new gallery.", today.strftime('%d %b %Y'), "https://nscd.gov.in/"),
            (2, "Creative Hobby Camps", "Summer workshops for budding scientists now enrolling in Mumbai.", (today - timedelta(days=1)).strftime('%d %b %Y'), "https://nehrusciencecentre.gov.in/"),
            (3, "Science on Wheels", "BITM Kolkata's mobile exhibition is touring North Bengal this month.", (today - timedelta(days=2)).strftime('%d %b %Y'), "https://bitm.gov.in/"),
            (4, "Robotics Gallery Launch", "A world-class robotics gallery featuring humanoid guides at Ahmedabad.", (today - timedelta(days=3)).strftime('%d %b %Y'), "https://sciencecity.gujarat.gov.in/"),
            (1, "Innovation Hub Membership", "Exclusive access to 3D printing and labs at the Delhi Innovation Hub.", today.strftime('%d %b %Y'), "https://nscd.gov.in/"),
            (None, "International Museum Day", "Celebrating heritage across all NCSM units with free entry on May 18th.", today.strftime('%d %b %Y'), "https://ncsm.gov.in/")
        ]
        c.executemany('INSERT INTO announcements (museum_id, title, description, date_published, redirect_url) VALUES (?, ?, ?, ?, ?)', announcements)


    
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
    print("Database initialized successfully.")