import sqlite3

class SemanticMemory:
    def __init__(self, db_path="semantic_memory.db"):
        self.db_path = db_path
        self._create_table()

    def _create_table(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS facts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    key TEXT UNIQUE NOT NULL,
                    value TEXT NOT NULL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

    def store_fact(self, key: str, value: str):
        """Add or update a fact."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO facts (key, value, updated_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(key) DO UPDATE SET
                    value = excluded.value,
                    updated_at = excluded.updated_at
            """, (key, value))

    def get_fact(self, key: str):
        """Get a fact by key. Returns value or None."""
        with sqlite3.connect(self.db_path) as conn:
            result = conn.execute(
                "SELECT value FROM facts WHERE key = ?",
                (key,)
            ).fetchone()
            
            if result is None:
                return None
            return result[0]

    def get_all_facts(self):
        """Return all facts as a dict {key: value}."""
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute("SELECT key, value FROM facts").fetchall()
            return {row[0]: row[1] for row in rows}

    def count(self):
        """How many facts stored."""
        with sqlite3.connect(self.db_path) as conn:
            result = conn.execute("SELECT COUNT(*) FROM facts").fetchone()
            return result[0]