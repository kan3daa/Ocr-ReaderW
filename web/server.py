from flask import Flask, render_template, jsonify
import sqlite3, pandas as pd, sys, os
sys.path.insert(0, '../db')
from database import DB_PATH

app = Flask(__name__, template_folder='templates')

def get_placeholder_cover(isbn):
    return f"data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIwIiBoZWlnaHQ9IjE4MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSIjNjk2OTZGIi8+PHRleHQgeD0iNTAlIiB5PSI1MCUiIGZvbnQtZmFtaWx5PSJBcmlhbCIgZm9udC1zaXplPSIxNCIgZmlsbD0id2hpdGUiIHRleHQtYW5jaG9yPSJtaWRkbGUiPknyvZ09hdXRoZXI8L3RleHQ+PC9zdmc+"

@app.route('/')
def index():
    # ENVOIE LIVRES pour index.html
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql("SELECT * FROM books ORDER BY scan_date DESC LIMIT 20", conn)
    conn.close()
    books = df.to_dict('records')
    for book in books:
        if not book.get('couverture'):
            book['couverture'] = get_placeholder_cover(book['isbn'])
    return render_template('index.html', books=books)  # ← AJOUT books

@app.route('/api/books')
def api_books():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql("SELECT * FROM books ORDER BY scan_date DESC LIMIT 100", conn)
    conn.close()
    books = df.to_dict('records')
    for book in books:
        if not book.get('couverture'):
            book['couverture'] = get_placeholder_cover(book['isbn'])
    return jsonify(books)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
