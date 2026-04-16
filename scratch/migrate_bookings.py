import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'museum.db')

def migrate():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    print("Starting migration...")
    
    try:
        c.execute("ALTER TABLE bookings ADD COLUMN razorpay_order_id TEXT")
        print("Added razorpay_order_id")
    except sqlite3.OperationalError:
        print("razorpay_order_id already exists")
        
    try:
        c.execute("ALTER TABLE bookings ADD COLUMN razorpay_payment_id TEXT")
        print("Added razorpay_payment_id")
    except sqlite3.OperationalError:
        print("razorpay_payment_id already exists")
        
    try:
        c.execute("ALTER TABLE bookings ADD COLUMN razorpay_signature TEXT")
        print("Added razorpay_signature")
    except sqlite3.OperationalError:
        print("razorpay_signature already exists")

    conn.commit()
    conn.close()
    print("Migration complete.")

if __name__ == "__main__":
    migrate()
