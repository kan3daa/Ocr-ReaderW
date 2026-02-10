from services.books_api import get_book_info
import sys
sys.path.insert(0, '../db')
from database import save_scan

def handle_isbn(isbn: str):
    if len(isbn) != 13 or not isbn.isdigit():
        print(f"ISBN invalide : {isbn}")
        return None
    
    book = get_book_info(isbn)
    if not book:
        print(f"ISBN inconnu : {isbn}")
        return None
    
    # ROBUSTE: .get() partout !
    titre = book.get('titre', 'Sans titre')
    auteur = book.get('auteur', 'Inconnu')
    edition = book.get('edition', 'N/A')
    
    # SAUVEGARDE
    save_scan(isbn, book)
    
    # PRINT SANS CRASH
    print(f" {titre} - {auteur} ({edition})")
    return book
