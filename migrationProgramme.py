import sqlite3

def main():
    conn = sqlite3.connect('tutoring_app.db')
    cursor = conn.cursor()

    # Alter the table to add is_paid column
    cursor.execute("PRAGMA foreign_keys = 0")
    cursor.execute("ALTER TABLE TutoringSessions ADD COLUMN is_paid INTEGER DEFAULT 0")
    cursor.execute("PRAGMA foreign_keys = 1")
    
    # Update all current rows to set is_paid to 0
    cursor.execute("UPDATE TutoringSessions SET is_paid = 0 WHERE is_paid IS NULL")

    conn.commit()
    conn.close()

    print("Migration completed successfully!")

if __name__ == "__main__":
    main()
