import sqlite3
import os

# Path to your database
DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'museum.db')

def view_bookings():
    if not os.path.exists(DB_PATH):
        print(f"Error: Database not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    print("\n" + "="*80)
    print(f"{'ID':<4} | {'MUSEUM ID':<10} | {'VISITOR':<15} | {'DATE':<12} | {'TICKETS':<8} | {'STATUS':<12}")
    print("-" * 80)

    try:
        cursor.execute("SELECT * FROM bookings")
        rows = cursor.fetchall()

        if not rows:
            print("No bookings found in the database.")
        else:
            for row in rows:
                id_val = str(row['id'])
                ex_id = str(row['exhibition_id'])
                visitor = str(row['visitor_name'])
                date_val = str(row['visit_date'])
                tickets = str(row['num_tickets'])
                status = str(row['status'])
                print(f"{id_val:<4} | {ex_id:<10} | {visitor:<15} | {date_val:<12} | {tickets:<8} | {status:<12}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()
    print("="*80 + "\n")

if __name__ == "__main__":
    view_bookings()
