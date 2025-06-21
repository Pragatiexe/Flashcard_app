from datetime import datetime
import sqlite3

SCORE_FILE = "score_history.txt"
SCORE_DB = "score_history.db"


def init_score_db():
    conn = sqlite3.connect("score_history.db")
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS score_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            score INTEGER NOT NULL,
            total INTEGER NOT NULL,
            difficulty TEXT DEFAULT "General"
        )
    ''')
    conn.commit()
    conn.close()


def log_score(score, total, difficulty="General"):
    """Log the score to both a text file and SQLite database."""
    # Log to text file
    with open(SCORE_FILE, "a") as f:
        f.write(f"{datetime.now()} | Score: {score}/{total} | Difficulty: {difficulty}\n")

    # Log to SQLite DB
    conn = sqlite3.connect(SCORE_DB)
    c = conn.cursor()
    c.execute("INSERT INTO score_log (timestamp, score, total, difficulty) VALUES (?, ?, ?, ?)",
              (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), score, total, difficulty))
    conn.commit()
    conn.close()

def get_score_history():
    """Get score history from the text file."""
    try:
        with open(SCORE_FILE, "r") as file:
            return file.readlines()
    except FileNotFoundError:
        return []

def clear_score_history():
    """Clear the text-based score history log."""
    open(SCORE_FILE, "w").close()

def init_leaderboard_db():
    with sqlite3.connect("score_history.db") as conn:
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS leaderboard (
                difficulty TEXT PRIMARY KEY,
                high_score INTEGER
            )
        """)
        conn.commit()


def update_leaderboard(score, difficulty):
    with sqlite3.connect("score_history.db") as conn:
        c = conn.cursor()
        c.execute("SELECT high_score FROM leaderboard WHERE difficulty = ?", (difficulty,))
        row = c.fetchone()
        if not row or score > row[0]:
            c.execute("REPLACE INTO leaderboard (difficulty, high_score) VALUES (?, ?)", (difficulty, score))
            conn.commit()


def get_leaderboard():
    with sqlite3.connect("score_history.db") as conn:
        c = conn.cursor()
        c.execute("SELECT difficulty, high_score FROM leaderboard ORDER BY high_score DESC")
        return c.fetchall()
