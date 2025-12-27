"""
test_all_preprocessing.py

Prova diverse combinazioni di preprocessing per trovare quella giusta.
"""

import os
from PIL import Image, ImageGrab
import cv2
import numpy as np
import pygetwindow as gw
from dotenv import load_dotenv
from os import getenv as env
import pytesseract

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

load_dotenv()

WINDOW_TITLE = env("WINDOW_TITLE", "BlueStacks")
OUTPUT_DIR = "debug_screenshots/preprocessing_tests"

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

def get_window():
    windows = gw.getWindowsWithTitle(WINDOW_TITLE)
    if not windows:
        print(f"❌ Finestra '{WINDOW_TITLE}' non trovata!")
        return None
    return windows[0]

def test_rolls():
    """Prova diverse combinazioni per i rolls."""
    print("\n" + "="*60)
    print("TEST ROLLS - TUTTE LE COMBINAZIONI")
    print("="*60)
    
    window = get_window()
    if not window:
        return
    
    screenshot = ImageGrab.grab(bbox=(window.left, window.top, window.left + window.width, window.top + window.height))
    
    # Coordinate per i rolls
    x_percent, y_percent, right_percent, bottom_percent = (44, 93, 56, 96)
    
    x = int(window.width * (x_percent / 100))
    y = int(window.height * (y_percent / 100))
    right = int(window.width * (right_percent / 100))
    bottom = int(window.height * (bottom_percent / 100))
    
    region = screenshot.crop((x, y, right, bottom))
    
    # Salva originale
    region.save(os.path.join(OUTPUT_DIR, "rolls_0_original.png"))
    print(f"✓ Originale salvato")
    
    # Prova diverse combinazioni
    combinations = [
        {"name": "grayscale_only", "threshold": None, "invert": False, "scale": 3},
        {"name": "threshold_150", "threshold": 150, "invert": False, "scale": 3},
        {"name": "threshold_150_inv", "threshold": 150, "invert": True, "scale": 3},
        {"name": "threshold_200", "threshold": 200, "invert": False, "scale": 3},
        {"name": "threshold_200_inv", "threshold": 200, "invert": True, "scale": 3},
        {"name": "threshold_100", "threshold": 100, "invert": False, "scale": 3},
        {"name": "threshold_100_inv", "threshold": 100, "invert": True, "scale": 3},
        {"name": "otsu", "threshold": -1, "invert": False, "scale": 3},
        {"name": "otsu_inv", "threshold": -1, "invert": True, "scale": 3},
    ]
    
    best_result = None
    best_combo = None
    
    for i, combo in enumerate(combinations, 1):
        # Converti in grayscale
        gray = cv2.cvtColor(np.array(region), cv2.COLOR_RGB2GRAY)
        
        # Scala
        if combo["scale"] > 1:
            width = int(gray.shape[1] * combo["scale"])
            height = int(gray.shape[0] * combo["scale"])
            gray = cv2.resize(gray, (width, height), interpolation=cv2.INTER_LANCZOS4)
        
        # Threshold
        if combo["threshold"] == -1:
            # Otsu's method
            _, gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        elif combo["threshold"]:
            _, gray = cv2.threshold(gray, combo["threshold"], 255, cv2.THRESH_BINARY)
        
        # Inverti
        if combo["invert"]:
            gray = cv2.bitwise_not(gray)
        
        # Salva
        processed_pil = Image.fromarray(gray)
        filename = f"rolls_{i}_{combo['name']}.png"
        processed_pil.save(os.path.join(OUTPUT_DIR, filename))
        
        # OCR
        text = pytesseract.image_to_string(processed_pil, config='--psm 7 -c tessedit_char_whitelist="0123456789/"')
        text_clean = text.strip().replace(" ", "")
        
        if "/" in text_clean and len(text_clean) >= 3:
            print(f"✅ {combo['name']:20s} -> '{text_clean}'")
            if not best_result:
                best_result = text_clean
                best_combo = combo
        else:
            print(f"❌ {combo['name']:20s} -> '{text_clean}'")
    
    if best_combo:
        print(f"\n🏆 MIGLIORE: {best_combo['name']} = '{best_result}'")
        print(f"   Impostazioni: threshold={best_combo['threshold']}, invert={best_combo['invert']}, scale={best_combo['scale']}")
    else:
        print(f"\n❌ Nessuna combinazione ha funzionato per i rolls")

def test_multiplier():
    """Prova diverse combinazioni per il multiplier."""
    print("\n" + "="*60)
    print("TEST MULTIPLIER - TUTTE LE COMBINAZIONI")
    print("="*60)
    
    window = get_window()
    if not window:
        return
    
    screenshot = ImageGrab.grab(bbox=(window.left, window.top, window.left + window.width, window.top + window.height))
    
    # Coordinate per il multiplier
    x_percent, y_percent, right_percent, bottom_percent = (53, 70, 57, 73)
    
    x = int(window.width * (x_percent / 100))
    y = int(window.height * (y_percent / 100))
    right = int(window.width * (right_percent / 100))
    bottom = int(window.height * (bottom_percent / 100))
    
    region = screenshot.crop((x, y, right, bottom))
    
    # Salva originale
    region.save(os.path.join(OUTPUT_DIR, "multi_0_original.png"))
    print(f"✓ Originale salvato")
    
    # Prova diverse combinazioni
    combinations = [
        {"name": "grayscale_only", "threshold": None, "invert": False, "scale": 3},
        {"name": "threshold_150", "threshold": 150, "invert": False, "scale": 3},
        {"name": "threshold_150_inv", "threshold": 150, "invert": True, "scale": 3},
        {"name": "threshold_200", "threshold": 200, "invert": False, "scale": 3},
        {"name": "threshold_200_inv", "threshold": 200, "invert": True, "scale": 3},
        {"name": "threshold_100", "threshold": 100, "invert": False, "scale": 3},
        {"name": "threshold_100_inv", "threshold": 100, "invert": True, "scale": 3},
        {"name": "otsu", "threshold": -1, "invert": False, "scale": 3},
        {"name": "otsu_inv", "threshold": -1, "invert": True, "scale": 3},
    ]
    
    best_result = None
    best_combo = None
    
    for i, combo in enumerate(combinations, 1):
        # Converti in grayscale
        gray = cv2.cvtColor(np.array(region), cv2.COLOR_RGB2GRAY)
        
        # Scala
        if combo["scale"] > 1:
            width = int(gray.shape[1] * combo["scale"])
            height = int(gray.shape[0] * combo["scale"])
            gray = cv2.resize(gray, (width, height), interpolation=cv2.INTER_LANCZOS4)
        
        # Threshold
        if combo["threshold"] == -1:
            # Otsu's method
            _, gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        elif combo["threshold"]:
            _, gray = cv2.threshold(gray, combo["threshold"], 255, cv2.THRESH_BINARY)
        
        # Inverti
        if combo["invert"]:
            gray = cv2.bitwise_not(gray)
        
        # Salva
        processed_pil = Image.fromarray(gray)
        filename = f"multi_{i}_{combo['name']}.png"
        processed_pil.save(os.path.join(OUTPUT_DIR, filename))
        
        # OCR
        text = pytesseract.image_to_string(processed_pil, config='--psm 7 -c tessedit_char_whitelist="x0123456789"')
        text_clean = text.strip().replace(" ", "")
        
        if "x" in text_clean.lower() or text_clean.isdigit():
            print(f"✅ {combo['name']:20s} -> '{text_clean}'")
            if not best_result:
                best_result = text_clean
                best_combo = combo
        else:
            print(f"❌ {combo['name']:20s} -> '{text_clean}'")
    
    if best_combo:
        print(f"\n🏆 MIGLIORE: {best_combo['name']} = '{best_result}'")
        print(f"   Impostazioni: threshold={best_combo['threshold']}, invert={best_combo['invert']}, scale={best_combo['scale']}")
    else:
        print(f"\n❌ Nessuna combinazione ha funzionato per il multiplier")

if __name__ == "__main__":
    print("Assicurati di essere nella schermata HOME del gioco!")
    input("Premi ENTER per iniziare...")
    
    test_rolls()
    test_multiplier()
    
    print(f"\n✓ Tutte le immagini di test sono in: {OUTPUT_DIR}")
    print("  Confronta le immagini per vedere quale preprocessing funziona meglio!")
