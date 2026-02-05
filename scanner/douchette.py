import re
import sys
from services.books_api import get_book_info


class DouchetteScanner:
    
    AZERTY_TO_DIGIT = {
        'ç':'9','è':'7','_':'8','é':'2','"':'3',
        '&':'1','(':'5',"'" : '4', '-' : '6','à':'0'
    }

    def azerty_to_isbn(self, s: str) -> str:
        return "".join(self.AZERTY_TO_DIGIT.get(c, c) for c in s)

    def clean_input(self, raw: str) -> str:
        return re.sub(
            r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])',
            '',
            raw
        ).strip()

    def scan_once(self):
        # Lecture de l'input
        raw = input("Scannez / entrez un ISBN : ")
        if not raw:
            print(" Entrée vide")
            return
        
        # Nettoyage et conversion AZERTY → chiffres
        cleaned = self.clean_input(raw)
        isbn = self.azerty_to_isbn(cleaned)

        print(f"ISBN décodé : '{isbn}'")
        
        # Vérification et récupération des infos
        if len(isbn) == 13 and isbn.isdigit():
            book = get_book_info(isbn)
            print(f"{book.get('titre','N/A')} - {book.get('auteur','N/A')} - {book.get('edition', book.get('Édition','N/A'))}")
            return book
        
        print("ISBN invalide")


def main():
    scanner = DouchetteScanner()

    while True:
        try:
            scanner.scan_once()
        except KeyboardInterrupt:
            print("\nArrêt du programme.")
            sys.exit(0)


if __name__ == "__main__":
    main()
