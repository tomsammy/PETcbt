import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "cbt.db")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Table for questions
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
    
    # Table for candidates
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
    
    # Table for submissions / results
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
        answers_json TEXT
    )
    """)
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Database initialized at:", DB_PATH)
