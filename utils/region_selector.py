import cv2
import numpy as np
import pygetwindow as gw
from mss import mss
from dotenv import load_dotenv
from os import getenv as env
import os
import sys
import pytesseract

# Load environment variables
# Assuming .env is in the parent directory (project root)
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
dotenv_path = os.path.join(project_root, ".env")
load_dotenv(dotenv_path)

# Tesseract Configuration
pytesseract.pytesseract.tesseract_cmd = r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe"

WINDOW_TITLE = env("WINDOW_TITLE")

def select_region():
    print(f"Looking for window with title: {WINDOW_TITLE}")
    try:
        windows = gw.getWindowsWithTitle(WINDOW_TITLE)
        if not windows:
            print(f"Error: Window '{WINDOW_TITLE}' not found.")
            return
        
        window = windows[0]
        print(f"Found window: {window.title} at ({window.left}, {window.top}, {window.width}, {window.height})")
        
        with mss() as sct:
            monitor = {
                "top": window.top,
                "left": window.left,
                "width": window.width,
                "height": window.height
            }
            
            sct_img = sct.grab(monitor)
            img = np.array(sct_img)
            img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
            
            print("\nINSTRUCTIONS:")
            print("1. A window will appear showing the game.")
            print("2. Use your mouse to DRAW A BOX around the Dice Number.")
            print("3. Press SPACE or ENTER to confirm.")
            print("4. Press 'c' to cancel.")
            
            roi = cv2.selectROI("Region Selector", img, showCrosshair=True, fromCenter=False)
            cv2.destroyAllWindows()
            
            x, y, w, h = roi
            
            if w == 0 or h == 0:
                print("Selection cancelled or invalid.")
                return

            # Perform OCR on the selected region
            roi_img = img[y:y+h, x:x+w]
            gray = cv2.cvtColor(roi_img, cv2.COLOR_BGR2GRAY)

            print("\n" + "="*40)
            print("OCR PREVIEW (Testing modes)")
            print("="*40)
            
            modes = [
                ("Original", roi_img),
                ("Inverted (White Text)", cv2.bitwise_not(roi_img)),
                ("Grayscale", gray),
                ("Binary Threshold", cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)[1]),
                ("Inv. Binary Threshold", cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)[1]),
                 # Otsu's thresholding automatically calculates the optimal threshold value
                ("Otsu Threshold", cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]),
                 ("Inv. Otsu Threshold", cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]),
            ]

            for name, image_mode in modes:
                text_raw = pytesseract.image_to_string(image_mode, config='--psm 6').strip()
                # text_digits = pytesseract.image_to_string(
                #     image_mode, 
                #     config=r'--psm 6 -c tessedit_char_whitelist="0123456789/"'
                # ).strip()
                
                # Only print if something was found to keep it clean, or print empty indicator
                print(f"Mode: {name:<25} | Result: '{text_raw}'")

            print("-" * 20)
            
            # Calculate percentages
            lp = (x / window.width) * 100
            tp = (y / window.height) * 100
            wp = (w / window.width) * 100
            hp = (h / window.height) * 100
            
            print("\n" + "="*40)
            print("SELECTED REGION (Percentage Coordinates)")
            print("="*40)
            print(f"Left(%):   {lp:.2f}")
            print(f"Top(%):    {tp:.2f}")
            print(f"Width(%):  {wp:.2f}")
            print(f"Height(%): {hp:.2f}")
            print("-" * 20)
            print(f"Tuple format: ({lp:.2f}, {tp:.2f}, {wp:.2f}, {hp:.2f})")
            print("="*40 + "\n")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    select_region()
