import requests
import time
import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin, quote


call_count = 0
last_call = 0

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}
def clean_isbn(isbn: str) -> str:
    """Nettoie un ISBN."""
    return re.sub(r"[^\d]", "", str(isbn))


def rate_limit():
    """Limite à 1 appel/sec."""
    global last_call
    now = time.time()
    delta = now - last_call
    if delta < 1:
        time.sleep(1 - delta)
    last_call = time.time()

def get_google_cover(isbn: str) -> str:
    """Fallback Google Books."""
    return f"https://books.google.com/books/content?vid=ISBN:{isbn}&printsec=frontcover&img=1&zoom=1"


def get_openlibrary_cover(isbn: str) -> str | None:
    """Récupère la couverture via OpenLibrary (stable mais base FR plus faible)."""
    url = f"https://covers.openlibrary.org/b/isbn/{isbn}-L.jpg"
    try:
        r = requests.get(url, timeout=5)
        if r.status_code == 200 and len(r.content) > 1000:
            print(f"[OPENLIBRARY] Cover OK: {isbn}")
            return url
    except Exception as e:
        print(f"[OPENLIBRARY] Erreur: {e}")
    return None


def get_amazon_cover(isbn: str) -> str | None:
    """Récupère la couverture via Amazon FR (fragile, dernier recours)."""
    url = f"https://www.amazon.fr/s?k={isbn}"
    headers = {
        "User-Agent": HEADERS["User-Agent"],
        "Accept-Language": "fr-FR,fr;q=0.9,en;q=0.8"
    }
    try:
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code != 200:
            print(f"[AMAZON] HTTP {r.status_code}")
            return None
        soup = BeautifulSoup(r.text, "html.parser")
        item = soup.select_one("div[data-component-type='s-search-result']")
        if not item:
            print("[AMAZON] Aucun résultat")
            return None
        img = item.select_one("img.s-image")
        if img and "images-amazon.com" in img.get("src", ""):
            print(f"[AMAZON] Cover OK: {isbn}")
            return img["src"]
    except Exception as e:
        print(f"[AMAZON] Erreur: {e}")
    return None


def get_book_info(isbn: str) -> dict:
    """Récupère titre, auteur, édition et couverture via multi-source."""
    global call_count
    call_count += 1
    isbn_clean = clean_isbn(isbn)
    rate_limit()

    url = f"https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn_clean}"

    try:
        resp = requests.get(url, timeout=8)
        if resp.status_code != 200:
            raise ValueError(f"[API] HTTP {resp.status_code}")
        data = resp.json()
        if not data.get("items"):
            raise ValueError("[API] Aucun résultat")
        vol = data["items"][0]["volumeInfo"]

        # Priorité couverture
        google_cover = vol.get("imageLinks", {}).get("thumbnail")
        cover = (
            google_cover
            or get_amazon_cover(isbn_clean)
            or get_openlibrary_cover(isbn_clean)
            or get_google_cover(isbn_clean)
        )

        return {
            "titre": vol.get("title", f"ISBN {isbn_clean}"),
            "auteur": vol.get("authors", ["N/A"])[0],
            "edition": vol.get("publisher", vol.get("publishedDate", "N/A")),
            "couverture": cover
        }

    except Exception as e:
        print(f"[API] Fallback: {e}")
        cover = get_amazon_cover(isbn_clean) or get_openlibrary_cover(isbn_clean) or get_google_cover(isbn_clean)
        return {
            "titre": f"ISBN {isbn_clean}",
            "auteur": "N/A",
            "edition": "N/A",
            "couverture": cover
        }