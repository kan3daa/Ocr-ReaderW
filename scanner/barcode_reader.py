import cv2
import pyzbar.pyzbar as pyzbar

def read_barcodes_from_frame(frame):
    if frame is None:
        return []
    barcodes = pyzbar.decode(frame)
    isbn_list = []
    for barcode in barcodes:
        isbn = barcode.data.decode('utf-8')
        isbn_list.append(isbn)
    return isbn_list
