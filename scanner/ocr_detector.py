import cv2
import time
import sys
import os
import numpy as np
import pytesseract

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from camera import Camera
from barcode_reader import read_barcodes_from_frame
from services.books_api import get_book_info, get_book_info_from_text

# ---------- Prétraitement ----------
def preprocess_for_ocr(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
    gray = clahe.apply(gray)
    gray = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY, 11, 2
    )
    gray = cv2.medianBlur(gray, 3)
    gray = cv2.bitwise_not(gray)  # texte noir sur fond blanc
    return gray

# ---------- Deskew ----------
def deskew(image):
    coords = np.column_stack(np.where(image > 0))
    if coords.size == 0:
        return image
    angle = cv2.minAreaRect(coords)[-1]
    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle
    (h, w) = image.shape[:2]
    M = cv2.getRotationMatrix2D((w//2, h//2), angle, 1.0)
    rotated = cv2.warpAffine(image, M, (w, h),
                            flags=cv2.INTER_CUBIC,
                            borderMode=cv2.BORDER_REPLICATE)
    return rotated

# ---------- OCR multi-PSM ----------
def ocr_best(roi):
    text = pytesseract.image_to_string(roi, lang="fra+eng")
    return text.replace("\n", " ").replace("\x0c", "").strip()


# ---------- Extraire titre et auteur ----------
def extract_title_author(frame):
    h, w, _ = frame.shape
    top = frame  # supprime la découpe des 30% supérieurs
    top = cv2.resize(top, None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC)  # super-resolution
    top = preprocess_for_ocr(top)
    top = deskew(top)

    contours, _ = cv2.findContours(top, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    blocks = []
    for cnt in contours:
        x, y, bw, bh = cv2.boundingRect(cnt)
        if bw > w*0.2*3 and bh > h*0.03*3:  # filtre taille bloc (×3 car resize)
            blocks.append((y, x, bw, bh))
    blocks.sort(key=lambda b: b[0])

    title, author = "", ""
    if blocks:
        y, x, bw, bh = blocks[0]
        roi = top[y:y+bh, x:x+bw]
        title = ocr_best(roi)
        if len(blocks) > 1:
            y, x, bw, bh = blocks[1]
            roi = top[y:y+bh, x:x+bw]
            author = ocr_best(roi)
    return title, author

# ---------- Main Detector ----------
def run_detector():
    cam = Camera(1)
    cam.open()
    BARCODE_COOLDOWN = 2
    OCR_COOLDOWN = 4
    last_barcode_time = 0
    last_ocr_time = 0
    last_isbn = None
    last_ocr_text = None
    try:
        while True:
            frame = cam.capture_frame()
            if frame is None:
                continue
            now = time.time()

            # --- Détection barcode ---
            codes = read_barcodes_from_frame(frame)
            if codes and (now - last_barcode_time) > BARCODE_COOLDOWN:
                last_barcode_time = now
                isbn = codes[0]
                if isbn != last_isbn:
                    last_isbn = isbn
                    try:
                        book = get_book_info(isbn)
                        print("\n=== ISBN détecté ===")
                        print(f"Titre : {book['titre']}")
                        print(f"Auteur : {book['auteur']}")
                        print(f"Edition : {book['edition']}")
                        print("====================\n")
                    except Exception as e:
                        print(f"Erreur API ISBN : {e}")

            # --- OCR titre/auteur ---
            elif (now - last_ocr_time) > OCR_COOLDOWN:
                last_ocr_time = now
                title, author = extract_title_author(frame)
                if title and title != last_ocr_text:
                    last_ocr_text = title
                    print("\n=== OCR détecté ===")
                    print(f"Titre : {title}")
                    print(f"Auteur : {author}")
                    print("===================\n")

            # --- Affichage vidéo ---
            cv2.imshow("Scanner", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    except KeyboardInterrupt:
        pass
    finally:
        cam.close()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    run_detector()
    