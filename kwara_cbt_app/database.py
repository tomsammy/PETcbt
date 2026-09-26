import os
import shutil
import re
import logging
from datetime import datetime

logger = logging.getLogger("cbt_database")

NEON_FALLBACK_URL = "postgresql://neondb_owner:npg_Rl0zv1crIkTY@ep-purple-heart-axjsakzf-pooler.c-4.us-east-2.aws.neon.tech/neondb?sslmode=require"

DATABASE_URL = (
    os.environ.get("DATABASE_URL") or
    os.environ.get("POSTGRES_URL") or
    os.environ.get("NEON_URL") or
    NEON_FALLBACK_URL
).strip()

# Normalize postgres:// to postgresql://
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

IS_POSTGRES = bool(DATABASE_URL and ("postgres" in DATABASE_URL or "neon.tech" in DATABASE_URL))

# SQLite DB Path fallback
if os.environ.get("VERCEL"):
    SQLITE_PATH = "/tmp/cbt.db"
    bundled_db = os.path.join(os.path.dirname(__file__), "cbt.db")
    if not os.path.exists(SQLITE_PATH) and os.path.exists(bundled_db):
        try:
            shutil.copyfile(bundled_db, SQLITE_PATH)
        except Exception:
            pass
else:
    SQLITE_PATH = os.path.join(os.path.dirname(__file__), "cbt.db")

class PostgresCursorWrapper:
    def __init__(self, raw_cursor):
        self.cursor = raw_cursor
        self.lastrowid = None

    def _convert_sql(self, sql):
        # Convert SQLite ? parameters to Postgres %s
        converted = sql.replace("?", "%s")
        # Handle auto-increment id return on inserts
        sql_upper = converted.upper()
        if "INSERT INTO" in sql_upper and "RETURNING" not in sql_upper:
            table_match = re.search(r"INSERT\s+INTO\s+(\w+)", converted, re.IGNORECASE)
            if table_match and table_match.group(1).lower() in ["candidates", "submissions"]:
                converted = converted.rstrip("; ") + " RETURNING id"
        return converted

    def execute(self, sql, params=None):
        sql_pg = self._convert_sql(sql)
        if params is not None:
            self.cursor.execute(sql_pg, params)
        else:
            self.cursor.execute(sql_pg)

        if "RETURNING id" in sql_pg:
            try:
                row = self.cursor.fetchone()
                if row:
                    self.lastrowid = row.get("id") if isinstance(row, dict) else row[0]
            except Exception:
                pass
        return self

    def executemany(self, sql, seq_of_parameters):
        sql_pg = sql.replace("?", "%s")
        return self.cursor.executemany(sql_pg, seq_of_parameters)

    def fetchone(self):
        return self.cursor.fetchone()

    def fetchall(self):
        return self.cursor.fetchall()

    @property
    def rowcount(self):
        return self.cursor.rowcount

    def close(self):
        try:
            self.cursor.close()
        except Exception:
            pass

class PostgresConnectionWrapper:
    def __init__(self, raw_conn):
        self.conn = raw_conn

    def cursor(self):
        import psycopg2.extras
        raw_cursor = self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        return PostgresCursorWrapper(raw_cursor)

    def commit(self):
        self.conn.commit()

    def rollback(self):
        self.conn.rollback()

    def close(self):
        self.conn.close()

def get_db_connection():
    if IS_POSTGRES:
        import psycopg2
        import psycopg2.extras
        import time
        last_err = None
        for attempt in range(3):
            try:
                conn = psycopg2.connect(DATABASE_URL, sslmode="require", connect_timeout=10)
                return PostgresConnectionWrapper(conn)
            except Exception as e:
                last_err = e
                time.sleep(1.0 * (attempt + 1))
        # If not running on Vercel and local SQLite database exists, gracefully fallback
        if not os.environ.get("VERCEL") and os.path.exists(SQLITE_PATH):
            import sqlite3
            logger.warning(f"Postgres connection timed out ({last_err}), falling back to local SQLite.")
            conn = sqlite3.connect(SQLITE_PATH)
            conn.row_factory = sqlite3.Row
            return conn
        raise last_err
    else:
        import sqlite3
        conn = sqlite3.connect(SQLITE_PATH)
        conn.row_factory = sqlite3.Row
        return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    if IS_POSTGRES:
        # PostgreSQL (Neon) Schema
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS questions (
            id SERIAL PRIMARY KEY,
            grade_level VARCHAR(50) NOT NULL,
            question_number INT NOT NULL,
            question_text TEXT NOT NULL,
            option_a TEXT NOT NULL,
            option_b TEXT NOT NULL,
            option_c TEXT NOT NULL,
            option_d TEXT NOT NULL,
            correct_answer VARCHAR(10) NOT NULL
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS candidates (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            psn VARCHAR(50) NOT NULL,
            email VARCHAR(255) NOT NULL,
            grade_level VARCHAR(50) NOT NULL,
            mda VARCHAR(255) DEFAULT 'State Civil Service',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS submissions (
            id SERIAL PRIMARY KEY,
            candidate_id INT,
            candidate_name VARCHAR(255) NOT NULL,
            psn VARCHAR(50) NOT NULL,
            email VARCHAR(255) NOT NULL,
            grade_level VARCHAR(50) NOT NULL,
            mda VARCHAR(255) DEFAULT 'State Civil Service',
            total_questions INT NOT NULL,
            correct_count INT NOT NULL,
            score_percentage NUMERIC(6,2) NOT NULL,
            grade_remark VARCHAR(100) NOT NULL,
            time_taken_seconds INT DEFAULT 0,
            submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            answers_json TEXT,
            violations_count INT DEFAULT 0,
            security_flags TEXT
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS system_settings (
            setting_key VARCHAR(100) PRIMARY KEY,
            setting_value TEXT NOT NULL
        )
        """)

        cursor.execute("""
        INSERT INTO system_settings (setting_key, setting_value)
        VALUES ('exam_status', 'open')
        ON CONFLICT (setting_key) DO NOTHING
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS demo_practice_logs (
            id SERIAL PRIMARY KEY,
            session_id VARCHAR(100) UNIQUE,
            psn VARCHAR(50),
            candidate_name VARCHAR(255),
            mda VARCHAR(255),
            grade_level VARCHAR(50),
            device_type VARCHAR(50),
            user_agent TEXT,
            ip_address VARCHAR(100),
            started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            submitted_at TIMESTAMP,
            total_questions INT DEFAULT 40,
            answered_count INT DEFAULT 0,
            correct_count INT DEFAULT 0,
            score_percentage NUMERIC(6,2) DEFAULT 0.0,
            time_taken_seconds INT DEFAULT 0,
            violations_count INT DEFAULT 0,
            violation_logs TEXT,
            status VARCHAR(50) DEFAULT 'in_progress'
        );
        CREATE INDEX IF NOT EXISTS idx_demo_psn ON demo_practice_logs(psn);
        CREATE INDEX IF NOT EXISTS idx_demo_started ON demo_practice_logs(started_at);
        """)

        conn.commit()

        # Seed questions if empty
        # Ensure candidate_roster has amended_psn column
        try:
            cursor.execute("ALTER TABLE candidate_roster ADD COLUMN IF NOT EXISTS amended_psn VARCHAR(50)")
            cursor.execute("ALTER TABLE candidate_roster ADD COLUMN IF NOT EXISTS amended_rank VARCHAR(255)")
            cursor.execute("ALTER TABLE candidate_roster ADD COLUMN IF NOT EXISTS amended_gl VARCHAR(10)")
            cursor.execute("ALTER TABLE candidate_roster ADD COLUMN IF NOT EXISTS amended_group VARCHAR(50)")
            cursor.execute("ALTER TABLE candidate_roster ADD COLUMN IF NOT EXISTS amended_exam_code VARCHAR(100)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_roster_amended_psn ON candidate_roster(amended_psn)")
            cursor.execute("ALTER TABLE submissions ADD COLUMN IF NOT EXISTS violations_count INT DEFAULT 0")
            cursor.execute("ALTER TABLE submissions ADD COLUMN IF NOT EXISTS security_flags TEXT")
            conn.commit()
        except Exception as e:
            logger.warning(f"Could not auto-add amended columns to Postgres candidate_roster or submissions: {e}")

        cursor.execute("SELECT COUNT(*) AS cnt FROM questions")
        row = cursor.fetchone()
        cnt = row["cnt"] if isinstance(row, dict) else row[0]
        if cnt == 0:
            try:
                from parser import seed_database
                seed_database()
            except Exception as e:
                logger.warning(f"Could not auto-seed Postgres: {e}")

    else:
        # SQLite Schema
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            grade_level TEXT NOT NULL,
            question_number INTEGER NOT NULL,
            question_text TEXT NOT NULL,
            option_a TEXT NOT NULL,
            option_b TEXT NOT NULL,
            option_c TEXT NOT NULL,
            option_d TEXT NOT NULL,
            correct_answer TEXT NOT NULL
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS candidates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            psn TEXT NOT NULL,
            email TEXT NOT NULL,
            grade_level TEXT NOT NULL,
            mda TEXT DEFAULT 'State Civil Service',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS submissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            candidate_id INTEGER,
            candidate_name TEXT NOT NULL,
            psn TEXT NOT NULL,
            email TEXT NOT NULL,
            grade_level TEXT NOT NULL,
            mda TEXT DEFAULT 'State Civil Service',
            total_questions INTEGER NOT NULL,
            correct_count INTEGER NOT NULL,
            score_percentage REAL NOT NULL,
            grade_remark TEXT NOT NULL,
            time_taken_seconds INTEGER DEFAULT 0,
            submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            answers_json TEXT,
            violations_count INTEGER DEFAULT 0,
            security_flags TEXT
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS system_settings (
            setting_key TEXT PRIMARY KEY,
            setting_value TEXT NOT NULL
        )
        """)

        cursor.execute("""
        INSERT OR IGNORE INTO system_settings (setting_key, setting_value)
        VALUES ('exam_status', 'open')
        """)

        # Ensure candidate_roster has amended_psn column
        try:
            cursor.execute("PRAGMA table_info(candidate_roster)")
            cols = [r[1] for r in cursor.fetchall()]
            if "amended_psn" not in cols:
                cursor.execute("ALTER TABLE candidate_roster ADD COLUMN amended_psn TEXT")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_roster_amended_psn ON candidate_roster(amended_psn)")
            if "amended_rank" not in cols:
                cursor.execute("ALTER TABLE candidate_roster ADD COLUMN amended_rank TEXT")
            if "amended_gl" not in cols:
                cursor.execute("ALTER TABLE candidate_roster ADD COLUMN amended_gl TEXT")
            if "amended_group" not in cols:
                cursor.execute("ALTER TABLE candidate_roster ADD COLUMN amended_group TEXT")
            if "amended_exam_code" not in cols:
                cursor.execute("ALTER TABLE candidate_roster ADD COLUMN amended_exam_code TEXT")
            cursor.execute("PRAGMA table_info(submissions)")
            sub_cols = [r[1] for r in cursor.fetchall()]
            if "violations_count" not in sub_cols:
                cursor.execute("ALTER TABLE submissions ADD COLUMN violations_count INTEGER DEFAULT 0")
            if "security_flags" not in sub_cols:
                cursor.execute("ALTER TABLE submissions ADD COLUMN security_flags TEXT")
            conn.commit()
        except Exception as e:
            logger.warning(f"Could not auto-add amended columns to SQLite candidate_roster or submissions: {e}")

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS demo_practice_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT UNIQUE,
            psn TEXT,
            candidate_name TEXT,
            mda TEXT,
            grade_level TEXT,
            device_type TEXT,
            user_agent TEXT,
            ip_address TEXT,
            started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            submitted_at TIMESTAMP,
            total_questions INTEGER DEFAULT 40,
            answered_count INTEGER DEFAULT 0,
            correct_count INTEGER DEFAULT 0,
            score_percentage REAL DEFAULT 0.0,
            time_taken_seconds INTEGER DEFAULT 0,
            violations_count INTEGER DEFAULT 0,
            violation_logs TEXT,
            status TEXT DEFAULT 'in_progress'
        );
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_demo_psn ON demo_practice_logs(psn);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_demo_started ON demo_practice_logs(started_at);")

        conn.commit()

    conn.close()

def get_setting(key: str, default: str = "") -> str:
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT setting_value FROM system_settings WHERE setting_key = ?", (key,))
        row = cursor.fetchone()
        conn.close()
        return row["setting_value"] if row else default
    except Exception:
        return default

def set_setting(key: str, value: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    if IS_POSTGRES:
        cursor.execute("""
        INSERT INTO system_settings (setting_key, setting_value)
        VALUES (%s, %s)
        ON CONFLICT (setting_key) DO UPDATE SET setting_value = EXCLUDED.setting_value
        """, (key, value))
    else:
        cursor.execute("""
        INSERT OR REPLACE INTO system_settings (setting_key, setting_value)
        VALUES (?, ?)
        """, (key, value))
    conn.commit()
    conn.close()
