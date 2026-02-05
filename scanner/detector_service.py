import cv2
import time
from datetime import datetime, timedelta
from scanner.camera import Camera
from scanner.barcode_reader import read_barcodes_from_frame
from services.books_api import get_book_info
from detector_service import DetectorService


class DetectorService:
    def scan(self, isbn: str) -> bool:
        return len(isbn) == 13 and isbn.isdigit()

def run_detector():
    last_scan_time = 0
    COOLDOWN = 5
    cam = Camera(1)
    cam.open()
    print("Camera OK")
    

    
while True:
    frame = cam.capture_frame()
    if frame is None:
        continue
    
    codes = read_barcodes_from_frame(frame)
    print(f"Nombres de codes detectes : {len(codes)}")
        
    if codes and (time.time() - last_scan_time) > COOLDOWN:
        last_scan_time = time.time()
        
        for code in codes:
            if not DetectorService().scan(code):
                continue  # ignorer les codes invalides
            
            info = get_book_info(code)
            print(f"NOUVEAU scan: {info.get('titre', 'N/A')}")
            
            cv2.putText(frame, f"{info.get('titre','N/A')}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(frame, f"Auteur: {info.get('auteur','N/A')}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            cv2.putText(frame, f"Édition: {info.get('edition', info.get('Édition','N/A'))}", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 2)
            
    else:
        if codes:
            print(" Cooldown actif")
                
    cv2.imshow('Scan', frame)
    
    if cv2.waitKey(1) == ord('q'):
        break
cam.close()
cv2.destroyAllWindows()
