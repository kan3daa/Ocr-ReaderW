import sqlite3
import os
from datetime import date

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(PROJECT_ROOT, "db", "data", "books.db")

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.executescript('''
        CREATE TABLE IF NOT EXISTS books (
            isbn TEXT PRIMARY KEY,
            titre TEXT NOT NULL,
            auteur TEXT,
            edition TEXT,
            scan_date DATE NOT NULL,
            scan_count INTEGER DEFAULT 1
        );
    ''')
    conn.commit()
    conn.close()
    print(f" DB: {DB_PATH}")

def save_scan(isbn, info):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        INSERT OR REPLACE INTO books 
        (isbn, titre, auteur, edition, scan_date, scan_count)
        VALUES (?, ?, ?, ?, DATE('now'), 
                COALESCE((SELECT scan_count+1 FROM books WHERE isbn=?), 1))
    ''', (isbn, info['titre'], info['auteur'], info.get('edition',''), isbn))
    conn.commit()
    conn.close()
    print(f" {info['titre'][:30]}...")
