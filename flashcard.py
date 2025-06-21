import sqlite3

DB_NAME = "flashcards.db"

def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS flashcards (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question TEXT NOT NULL,
                answer TEXT NOT NULL,
                category TEXT DEFAULT 'General'
            )
        ''')
        conn.commit()

def add_flashcard_db(question, answer, category="General"):
    with sqlite3.connect(DB_NAME) as conn:
        c = conn.cursor()
        c.execute("INSERT INTO flashcards (question, answer, category) VALUES (?, ?, ?)", (question, answer, category))
        conn.commit()

def get_all_flashcards():
    with sqlite3.connect(DB_NAME) as conn:
        c = conn.cursor()
        c.execute("SELECT id, question, answer, category FROM flashcards")
        rows = c.fetchall()
        return [{"id": row[0], "question": row[1], "answer": row[2], "category": row[3]} for row in rows]

def update_flashcard(flashcard_id, new_question, new_answer, new_category):
    with sqlite3.connect(DB_NAME) as conn:
        c = conn.cursor()
        c.execute("UPDATE flashcards SET question = ?, answer = ?, category = ? WHERE id = ?", (new_question, new_answer, new_category, flashcard_id))
        conn.commit()
