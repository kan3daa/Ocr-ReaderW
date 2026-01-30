from scanner.camera import Camera
from scanner.barcode_reader import read_barcodes_from_frame

cam = Camera(1)  # force index 0
cam.open()
frame = cam.capture_frame()
codes = read_barcodes_from_frame(frame)
print(f"Codes trouvés : {codes}")
cam.close()
