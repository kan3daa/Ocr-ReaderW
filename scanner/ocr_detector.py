import cv2
import time
import sys
import os
import pytesseract

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from camera import Camera
from barcode_reader import read_barcodes_from_frame
from services.books_api import get_book_info

def extract_text_from_frame(frame):
    if frame is None:
        return ""
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.resize(
        gray,
        None,
        fx=2,
        fy=2,
        interpolation=cv2.INTER_CUBIC
    )
    gray = cv2.adaptiveThreshold(
        gray,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        11,
        2
    )
    config = "--oem 3 --psm 6 -l fra+eng"
    text = pytesseract.image_to_string(gray, config=config)
    return text.strip()

def run_detector():
    cam = Camera(1)
    cam.open()
    print("Camera OK (index 0)")

    last_scan_time = 0
    COOLDOWN = 2
    codes = []

    try:
        while True:
            frame = cam.capture_frame()
            if frame is None:
                continue
            
            # ocr
            ocr_text = extract_text_from_frame(frame)

            codes = read_barcodes_from_frame(frame)

            if codes and (time.time() - last_scan_time) > COOLDOWN:
                last_scan_time = time.time()
                for code in codes:
                    book = get_book_info(code)
                    if book:
                        print(f"ISBN: {code}")
                        print(f"Titre API: {book.get('titre', 'N/A')}")
                        print(f"Auteur API: {book.get('auteur', 'N/A')}")
                        print(f"Edition API: {book.get('edition', 'N/A')}")
                        print("OCR détecté sur la couverture :")
                        print(ocr_text[:200])

            cv2.imshow('Scanner OCR', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    except KeyboardInterrupt:
        print("Arrêt manuel")
    finally:
        cam.close()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    run_detector()