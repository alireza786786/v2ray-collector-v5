import sqlite3
import threading

class Database:
    def __init__(self, db_path="history.db"):
        self.db_path = db_path
        self.lock = threading.Lock()
        self._init_db()

    def _init_db(self):
        with self.lock, sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS history (
                    node_key TEXT PRIMARY KEY,
                    ewma_score REAL,
                    samples INTEGER
                )
            """)
            conn.commit()

    def get_score(self, node_key):
        with self.lock, sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT ewma_score, samples FROM history WHERE node_key = ?", (node_key,))
            row = cursor.fetchone()
            if row:
                return row[0], row[1]
            return None, 0

    def update_score(self, node_key, current_score, decay=0.7):
        with self.lock, sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT ewma_score, samples FROM history WHERE node_key = ?", (node_key,))
            row = cursor.fetchone()
            if row:
                old_score, samples = row
                new_score = decay * old_score + (1 - decay) * current_score
                new_samples = samples + 1
                cursor.execute("UPDATE history SET ewma_score = ?, samples = ? WHERE node_key = ?", (new_score, new_samples, node_key))
            else:
                cursor.execute("INSERT INTO history (node_key, ewma_score, samples) VALUES (?, ?, ?)", (node_key, current_score, 1))
            conn.commit()
