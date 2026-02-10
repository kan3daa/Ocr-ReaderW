import cv2
import pyzbar.pyzbar as pyzbar
from pyzbar.pyzbar import ZBarSymbol  # Pour cibler EAN13
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

def read_barcodes_from_frame(frame):
    if frame is None: return []
    
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5,5), 0)
    thresh = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    
    barcodes = pyzbar.decode(thresh, symbols=[
        ZBarSymbol.EAN13, ZBarSymbol.UPCA, ZBarSymbol.EAN8, ZBarSymbol.I25
    ])
    
    isbn_list = []
    for barcode in barcodes:
        code = barcode.data.decode('utf-8')
        
        if code.isdigit() and 10 <= len(code) <= 13:
            isbn_list.append(code)
            print(f"Code: {code} (type: {barcode.type})")
    
    return isbn_list

