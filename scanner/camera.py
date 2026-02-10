import cv2
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

class Camera:
    def __init__(self, camera_index=1):
        self.camera_index = camera_index
        self.cap = None

    def open(self):
        self.cap = cv2.VideoCapture(self.camera_index)
        if not self.cap.isOpened():
            raise Exception(f"Could not open camera with index {self.camera_index}")

    def close(self):
        if self.cap:
            self.cap.release()
            self.cap = None
            
    def capture_frame(self):
        if self.cap is None:
            self.cap = cv2.VideoCapture(self.camera_index)
    
        ret, frame = self.cap.read()
        return frame


