import re
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)) + '/db')
from database import save_scan, init_db
from scanner.handlers import handle_isbn

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
        raw = input("Scannez / entrez un ISBN : ")
        if not raw:
            print("Entrée vide")
            return
        
        cleaned = self.clean_input(raw)
        isbn = self.azerty_to_isbn(cleaned)
        print(f"ISBN décodé : '{isbn}'")

        # Ici on délègue:
        return handle_isbn(isbn)

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
