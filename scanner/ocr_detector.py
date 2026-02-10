import cv2
import time
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from camera import Camera
from barcode_reader import read_barcodes_from_frame
from services.books_api import get_book_info


def run_detector():
    cam = Camera(1)
    cam.open()
    print(" Camera OK (index 1)")
    
    last_scan_time = 0
    COOLDOWN = 2  # réduit
    
    try:
        while True:
            frame = cam.capture_frame()
            if frame is None:
                print(" Frame vide")
                continue
            
            codes = read_barcodes_from_frame(frame)
            print(f"Codes: {len(codes)}")
            
            if codes and (time.time() - last_scan_time) > COOLDOWN:
                last_scan_time = time.time()
                for code in codes:
                    book = get_book_info(code)
                    if book:
                        print(f"{book.get('titre', 'N/A')}, {book.get('auteur', 'N/A')}, {book.get('edition', 'N/A')}")
            
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
