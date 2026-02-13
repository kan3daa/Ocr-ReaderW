from flask import Flask, render_template, jsonify
import sqlite3
import pandas as pd
import sys, os



# Ajout du chemin vers services pour books_api
sys.path.insert(0, os.path.abspath('../services'))
from books_api import get_book_info

# Chemin vers ta base SQLite
sys.path.insert(0, '../db')
from database import DB_PATH

app = Flask(__name__, template_folder='templates')

def get_placeholder_cover(isbn):
    """Image par défaut si aucune couverture disponible."""
    return (
        '/static/default-cover.png'
    )

@app.route('/')
def index():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql("SELECT * FROM books ORDER BY scan_date DESC LIMIT 20", conn)
    conn.close()
    books = df.to_dict('records')

    # Complète les couvertures manquantes
    for book in books:
        if not book.get('couverture'):
            info = get_book_info(book['isbn'])
            book['couverture'] = info['couverture'] or get_placeholder_cover(book['isbn'])

    return render_template('index.html', books=books)

@app.route('/api/books')
def api_books():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql("SELECT * FROM books ORDER BY scan_date DESC LIMIT 100", conn)
    conn.close()
    books = df.to_dict('records')

    for book in books:
        if not book.get('couverture'):
            info = get_book_info(book['isbn'])
            book['couverture'] = info['couverture'] or get_placeholder_cover(book['isbn'])

    return jsonify(books)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
