import cv2
from scanner.camera import Camera
from scanner.barcode_reader import read_barcodes_from_frame
from services.books_api import get_book_info
import time
from datetime import datetime, timedelta

def run_detector():
    last_scan_time = 0
    COOLDOWN = 10
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
                info = get_book_info(code)
                print(f" NOUVEAU scan: {info['titre']}")
                
                cv2.putText(frame, f"{info['titre']}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                cv2.putText(frame, f"Auteur: {info['auteur']}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                cv2.putText(frame, f"Édition: {info['edition']}", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 2)
                
        else:
            if codes:
                print(" Cooldown actif")
                    
        cv2.imshow('Scan', frame)
        
        if cv2.waitKey(1) == ord('q'):
            break
    cam.close()
    cv2.destroyAllWindows()