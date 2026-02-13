import requests
import re
import os
from urllib.parse import quote
import time

# =========================
# CONFIGURATION
# =========================
API_KEY = os.environ.get("GOOGLE_BOOKS_KEY")  # Clé API Google Books
PLACEHOLDER_COVER = "/static/default-cover.png"  # Image par défaut si tout échoue

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept-Language": "fr-FR,fr;q=0.9"
}

session = requests.Session()
session.headers.update(HEADERS)

_last_call = 0
_cache_isbn: dict[str, dict] = {}  # Cache local pour ISBN
_cache_text: dict[str, dict] = {}  # Cache local pour texte OCR

# =========================
# UTILITAIRES
# =========================
def clean_isbn(isbn: str) -> str:
    """Supprime tout caractère autre que les chiffres d'un ISBN."""
    return re.sub(r"[^\d]", "", str(isbn))

def format_isbn13_with_dashes(isbn: str) -> str:
    """Formate un ISBN-13 pour GeoBib (avec tirets)."""
    isbn = clean_isbn(isbn)
    if len(isbn) != 13:
        return isbn
    return f"{isbn[0:3]}-{isbn[3]}-{isbn[4:7]}-{isbn[7:12]}-{isbn[12]}"

def rate_limit():
    """Limiter les appels à 2 requêtes/sec pour éviter blocage."""
    global _last_call
    now = time.time()
    delta = now - _last_call
    if delta < 0.5:
        time.sleep(0.5 - delta)
    _last_call = time.time()

def safe_get_json(url: str, timeout: int = 5) -> dict | None:
    """Effectue une requête GET JSON sécurisée avec rate-limit."""
    try:
        rate_limit()
        resp = session.get(url, timeout=timeout)
        if resp.status_code == 200:
            return resp.json()
    except requests.RequestException:
        pass
    return None

# =========================
# COUVERTURES
# =========================
def get_geobib_cover(isbn: str, size="small") -> str | None:
    """Renvoie l'URL directe de l'image GeoBib. Reçoit ISBN avec tirets."""
    isbn_dash = format_isbn13_with_dashes(isbn)
    return f"https://couverture.geobib.fr/api/v1/{isbn_dash}/{size}"

def get_decitre_cover(isbn: str) -> str | None:
    """Scrape Decitre si GeoBib ne renvoie rien. Reçoit ISBN sans tirets."""
    isbn_clean = clean_isbn(isbn)
    url = f"https://www.decitre.fr/livres/{isbn_clean}.html"
    try:
        rate_limit()
        resp = session.get(url, timeout=5)
        if resp.status_code != 200:
            return None
        match = re.search(r'<img[^>]+src="([^"]+\.webp)"[^>]*class="image"', resp.text)
        if match:
            return match.group(1)
    except requests.RequestException:
        pass
    return None

def get_google_static_cover(isbn: str) -> str:
    """Fallback sur Google Books statique si tout échoue."""
    isbn_clean = clean_isbn(isbn)
    return f"https://books.google.com/books/content?vid=ISBN:{isbn_clean}&printsec=frontcover&img=1&zoom=1"

def resolve_cover(isbn: str, google_cover: str | None = None) -> str:
    """
    Détermine la meilleure couverture disponible :
    GeoBib → Decitre → Google → placeholder
    """
    # GeoBib prioritaire (avec tirets)
    cover = get_geobib_cover(isbn)
    if cover:
        return cover

    # Decitre reçoit ISBN sans tirets
    cover = get_decitre_cover(isbn)
    if cover:
        return cover

    if google_cover:
        return google_cover

    return PLACEHOLDER_COVER

# =========================
# API ISBN
# =========================
def get_book_info(isbn: str) -> dict:
    """Récupère les informations d'un livre via Google Books + couverture fallback."""
    isbn_clean = clean_isbn(isbn)

    if isbn_clean in _cache_isbn:
        return _cache_isbn[isbn_clean]

    url = f"https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn_clean}&key={API_KEY}"
    data = safe_get_json(url)

    if not data or not data.get("items"):
        result = {
            "titre": f"ISBN {isbn_clean}",
            "auteur": "N/A",
            "edition": "N/A",
            "isbn": isbn_clean,
            "couverture": resolve_cover(isbn_clean)
        }
        _cache_isbn[isbn_clean] = result
        return result

    vol = data["items"][0]["volumeInfo"]
    google_cover = vol.get("imageLinks", {}).get("thumbnail")

    result = {
        "titre": vol.get("title", f"ISBN {isbn_clean}"),
        "auteur": vol.get("authors", ["N/A"])[0],
        "edition": vol.get("publisher", vol.get("publishedDate", "N/A")),
        "isbn": isbn_clean,
        "couverture": resolve_cover(isbn_clean, google_cover)
    }

    _cache_isbn[isbn_clean] = result
    return result

# =========================
# API TEXTE (OCR)
# =========================
def get_book_info_from_text(text: str) -> dict | None:
    """Récupère les informations d'un livre depuis du texte OCR."""
    text = text.strip()
    if len(text) < 10:
        return None

    key = text[:50]
    if key in _cache_text:
        return _cache_text[key]

    query = quote(key)
    url = f"https://www.googleapis.com/books/v1/volumes?q=intitle:{query}+OR+inauthor:{query}&key={API_KEY}"
    data = safe_get_json(url)

    if not data or not data.get("items"):
        return None

    vol = data["items"][0]["volumeInfo"]
    identifiers = vol.get("industryIdentifiers", [{}])
    isbn_raw = identifiers[0].get("identifier", "") if identifiers else ""
    google_cover = vol.get("imageLinks", {}).get("thumbnail")

    result = {
        "titre": vol.get("title", "N/A"),
        "auteur": vol.get("authors", ["N/A"])[0],
        "edition": vol.get("publisher", "N/A"),
        "isbn": clean_isbn(isbn_raw),
        "couverture": resolve_cover(clean_isbn(isbn_raw), google_cover)
    }

    _cache_text[key] = result
    return result
