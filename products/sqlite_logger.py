import logging
import sqlite3
import os
from datetime import datetime

# Path to your SQLite database file (you can store it inside BASE_DIR)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, 'user_actions_logs.db')


class SQLiteHandler(logging.Handler):
    """Custom logging handler that stores logs in a single SQLite database table."""

    def __init__(self, db_path=DB_PATH):
        super().__init__()
        self.db_path = db_path
        self._create_table()

    def _create_table(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                level TEXT,
                created_at TEXT,
                module TEXT,
                message TEXT
            )
        ''')
        conn.commit()
        conn.close()

    def emit(self, record):
        try:
            log_entry = self.format(record)
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO logs (level, created_at, module, message) VALUES (?, ?, ?, ?)",
                (record.levelname, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), record.module, log_entry)
            )
            conn.commit()
        except Exception as e:
            print(f"Logging error: {e}")
        finally:
            conn.close()
