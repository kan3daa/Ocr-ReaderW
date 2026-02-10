import requests

def get_book_info(isbn):
    try:
        # Google Books
        r = requests.get(f'https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}', timeout=5)
        data = r.json()
        
        if data.get('items'):
            vol = data['items'][0]['volumeInfo']
            return {
                'titre': vol.get('title', 'Sans titre'),
                'auteur': vol.get('authors', ['Inconnu'])[0] if vol.get('authors') else 'Inconnu',
                'edition': vol.get('publisher', 'N/A'),
                'couverture': f"https://covers.openlibrary.org/b/isbn/{isbn}-M.jpg"
            }
    except:
        pass
    
    return {
        'titre': f'ISBN {isbn}',
        'auteur': 'Inconnu',
        'edition': 'N/A',
        'couverture': None
    }
