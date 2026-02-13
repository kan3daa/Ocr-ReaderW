import threading
import subprocess
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))


def run_douchette():
    subprocess.run([sys.executable, "-m", "scanner.douchette"])

def run_camera():
    subprocess.run([sys.executable, "scanner/ocr_detector.py"])

def main():
    print("Douchette (t1) + Caméra (t2)")
    
    t1 = threading.Thread(target=run_douchette, daemon=True)
    t2 = threading.Thread(target=run_camera, daemon=True)
    
    t1.start()
    t2.start()
    
    try:
        t1.join()
        t2.join()
    except KeyboardInterrupt:
        print("\n Arrêt des scanners")

if __name__ == "__main__":
    main()