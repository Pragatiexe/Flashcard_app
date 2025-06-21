import sqlite3

DB_NAME = "flashcards.db"

def init_db():
    conn = sqlite3.connect("flashcards.db")
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS flashcards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT NOT NULL,
            answer TEXT NOT NULL,
            category TEXT,
            difficulty TEXT
        )
    ''')
    conn.commit()
    conn.close()


def add_flashcard_db(question, answer, category="General", difficulty="Easy"):
    conn = sqlite3.connect("flashcards.db")
    c = conn.cursor()
    c.execute(
        "INSERT INTO flashcards (question, answer, category, difficulty) VALUES (?, ?, ?, ?)",
        (question, answer, category, difficulty)
    )
    conn.commit()
    conn.close()


def get_all_flashcards():
    conn = sqlite3.connect("flashcards.db")
    c = conn.cursor()
    c.execute("SELECT id, question, answer, category, difficulty FROM flashcards")
    rows = c.fetchall()
    conn.close()
    return [
        {
            "id": row[0],
            "question": row[1],
            "answer": row[2],
            "category": row[3] or "General",
            "difficulty": row[4] or "Easy"
        }
        for row in rows
    ]


def get_flashcard_by_id(flashcard_id):
    """
    Retrieve a specific flashcard by its ID.
    Returns a dictionary with id, question, and answer.
    """
    with sqlite3.connect(DB_NAME) as conn:
        c = conn.cursor()
        c.execute("SELECT id, question, answer FROM flashcards WHERE id = ?", (flashcard_id,))
        row = c.fetchone()
        if row:
            return {"id": row[0], "question": row[1], "answer": row[2]}
        return None

def delete_flashcard(flashcard_id):
    """
    Delete a flashcard by its ID.
    """
    with sqlite3.connect(DB_NAME) as conn:
        c = conn.cursor()
        c.execute("DELETE FROM flashcards WHERE id = ?", (flashcard_id,))
        conn.commit()

def update_flashcard(card_id, question, answer, category, difficulty):
    conn = sqlite3.connect("flashcards.db")
    c = conn.cursor()
    c.execute("""
        UPDATE flashcards
        SET question = ?, answer = ?, category = ?, difficulty = ?
        WHERE id = ?
    """, (question, answer, category, difficulty, card_id))
    conn.commit()
    conn.close()


