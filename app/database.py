# app/database.py

import sqlite3

DB_PATH = "database.db"

def connection():
    """Returns a new connection to the SQLite database."""
    return sqlite3.connect(DB_PATH, check_same_thread=False, timeout=10)

def does_db_exist():
    """Check if the database file exists."""
    try:
        conn = connection()
        c = conn.cursor()
        c.execute('''
            SHOW TABLES
        ''')
        tables = c.fetchall()
        conn.close()
        return len(tables) > 0
    except sqlite3.Error:
        return False

def create_db():
    """Create the database and tables if they do not exist."""

    conn = connection()
    c = conn.cursor()
    c.execute("DROP TABLE IF EXISTS media") # This would be replaced with an importing script which would do a comparaison in a real-world scenario
    c.execute('''
        CREATE TABLE media (
            media_id INTEGER PRIMARY KEY AUTOINCREMENT,
            id INTEGER,
            media_type TEXT NOT NULL CHECK(media_type IN ('movie', 'tv')),
            title TEXT,
            original_title TEXT,
            release_date TEXT,
            overview TEXT,
            poster_path TEXT,
            vote_average REAL
        )
    ''')
    c.execute("DROP TABLE IF EXISTS towatch") # This would be replaced with an importing script which would do a comparaison in a real-world scenario
    c.execute('''
        CREATE TABLE towatch (
            media_id INTEGER PRIMARY KEY AUTOINCREMENT,
            id INTEGER,
            media_type TEXT NOT NULL CHECK(media_type IN ('movie', 'tv')),
            title TEXT,
            original_title TEXT,
            release_date TEXT,
            overview TEXT,
            poster_path TEXT,
            vote_average REAL
        );
    ''')
    conn.commit()
    conn.close()
