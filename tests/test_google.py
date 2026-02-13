import os
import requests

API_KEY = os.environ.get("GOOGLE_BOOKS_KEY")
ISBN = "9782266297738"
url = f"https://www.googleapis.com/books/v1/volumes?q=isbn:{ISBN}&key={API_KEY}"

resp = requests.get(url)
if resp.status_code == 200:
    data = resp.json()
    if "items" in data and len(data["items"]) > 0:
        vol = data["items"][0]["volumeInfo"]
        print("Titre :", vol.get("title", "N/A"))
        print("Auteur :", vol.get("authors", ["N/A"])[0])
        print("Editeur :", vol.get("publisher", "N/A"))
        print("Couverture :", vol.get("imageLinks", {}).get("thumbnail"))
    else:
        print("Aucun résultat pour cet ISBN.")
else:
    print("Erreur API :", resp.status_code)
