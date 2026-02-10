from flask import Flask, render_template, jsonify
import sqlite3, pandas as pd, sys, os, requests
sys.path.insert(0, '../db')
from database import DB_PATH

app = Flask(__name__, template_folder='templates')

def get_cover_url(isbn):
    url = f"https://covers.openlibrary.org/b/isbn/{isbn}-M.jpg"
    return url  # Direct - fiable !

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/books')
def api_books():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql("SELECT * FROM books ORDER BY scan_date DESC LIMIT 100", conn)
    conn.close()
    
    for book in df.to_dict('records'):
        book['couverture'] = get_cover_url(book['isbn'])
    
    return jsonify(df.to_dict('records'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
