import sqlite3

# Connect to SQLite3 database (it will create 'tutoring_app.db' if it doesn't exist)
conn = sqlite3.connect('tutoring_app.db')
cursor = conn.cursor()

# Create Students table
cursor.execute('''
CREATE TABLE IF NOT EXISTS Students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    price_per_hour REAL NOT NULL
);
''')

# Create TutoringSessions table with is_paid column
cursor.execute('''
CREATE TABLE IF NOT EXISTS TutoringSessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    date_of_session DATE NOT NULL,
    hours_worked REAL NOT NULL,
    is_paid INTEGER DEFAULT 0,
    FOREIGN KEY (student_id) REFERENCES Students(id)
);
''')

# Commit the changes and close the connection
conn.commit()
conn.close()
