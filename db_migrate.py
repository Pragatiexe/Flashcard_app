import sqlite3

conn = sqlite3.connect("flashcards.db")
c = conn.cursor()

# Add 'category' column if it doesn't exist
try:
    c.execute("ALTER TABLE flashcards ADD COLUMN category TEXT")
    print("Added 'category' column.")
except sqlite3.OperationalError:
    print("'category' column already exists.")

# Add 'difficulty' column if it doesn't exist
try:
    c.execute("ALTER TABLE flashcards ADD COLUMN difficulty TEXT")
    print("Added 'difficulty' column.")
except sqlite3.OperationalError:
    print("'difficulty' column already exists.")

conn.commit()
conn.close()
print("Migration complete.")
