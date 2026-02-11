import cv2
import time
from scanner.camera import Camera
from scanner.barcode_reader import read_barcodes_from_frame
from services.books_api import get_book_info
import pytesseract

class DetectorService:
    def scan(self, isbn: str) -> bool:
        return len(isbn) == 13 and isbn.isdigit()
    
    @staticmethod
    def extract_text_from_frame(frame):
        if frame is None:
            return ""
        # Redimensionner pour l'OCR (640px de large)
        h, w = frame.shape[:2]
        scale = 640 / w
        resized = cv2.resize(frame, (640, int(h*scale)))
        gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
        gray = cv2.adaptiveThreshold(
            gray, 255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            11, 2
        )
        config = "--oem 3 --psm 6 -l fra+eng"
        text = pytesseract.image_to_string(gray, config=config)
        return text.strip()

def run_detector():
    cam = Camera(1)
    cam.open()
    print("Camera OK (q=quit)")

    last_scan_time = 0
    COOLDOWN = 5   # cooldown pour la détection ISBN/OCR

    try:
        while True:
            frame = cam.capture_frame()
            if frame is None:
                continue
            
            codes = read_barcodes_from_frame(frame)
            
            # Si on a des codes et que le cooldown est passé
            if codes and (time.time() - last_scan_time) > COOLDOWN:
                last_scan_time = time.time()
                
                for code in codes:
                    if not DetectorService().scan(code):
                        continue
                    
                    book = get_book_info(code)
                    print(f"ISBN: {code}")
                    print(f"Titre API: {book.get('titre', 'N/A')}")
                    print(f"Auteur API: {book.get('auteur', 'N/A')}")
                    print(f"Edition API: {book.get('edition', 'N/A')}")
                    
                    # OCR ponctuel seulement sur ce frame
                    ocr_text = DetectorService.extract_text_from_frame(frame)
                    print("OCR détecté sur la couverture (premiers 200 chars):")
                    print(ocr_text[:200])

            cv2.imshow('Scanner OCR', frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
    except KeyboardInterrupt:
        pass
    finally:
        cam.close()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    run_detector()
