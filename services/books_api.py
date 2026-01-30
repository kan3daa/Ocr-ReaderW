import requests

def get_book_info(isbn):
    response = requests.get(f'https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}')
    data = response.json()
    
    if not data.get("items"):
        return {"titre": f"ISBN inconnu : {isbn}", "auteur": "N/A"}
    
    volume = data["items"][0]["volumeInfo"]
    return {
        "titre": volume.get("title", "Sans titre"),
        "auteur": volume.get("authors", ["Inconnu"])[0],
        "edition" : volume.get("publisher", "Inconnue")
    }