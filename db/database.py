import sqlite3
from datetime import date

DB_PATH = "data/books.db"

def init_db():
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    with open('schema.sql') as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()

def save_scan(isbn, info):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        INSERT OR REPLACE INTO books 
        (isbn, titre, auteur, edition, scan_date, scan_count)
        VALUES (?, ?, ?, ?, DATE('now'), 
                COALESCE((SELECT scan_count+1 FROM books WHERE isbn=?), 1))
    ''', (isbn, info['titre'], info['auteur'], info['edition'], isbn))
    conn.commit()
    conn.close()
