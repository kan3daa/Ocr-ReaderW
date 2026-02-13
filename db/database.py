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
        INSERT INTO books (isbn, titre, auteur, edition, scan_date, scan_count)
        VALUES (?, ?, ?, ?, DATE('now'), 1)
        ON CONFLICT(isbn) DO UPDATE SET
            titre = excluded.titre,
            auteur = excluded.auteur,
            edition = excluded.edition,
            scan_date = DATE('now'),
            scan_count = books.scan_count + 1
    ''', (
        isbn,
        info['titre'],
        info['auteur'],
        info.get('edition', '')
    ))

    conn.commit()
    conn.close()

    print(f" {info['titre'][:30]}...")

