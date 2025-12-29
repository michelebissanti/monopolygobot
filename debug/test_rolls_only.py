"""
test_rolls_only.py

Test specifico per trovare le coordinate perfette dei rolls.
"""

import os
from PIL import Image, ImageGrab, ImageDraw
import cv2
import numpy as np
import pygetwindow as gw
from dotenv import load_dotenv
from os import getenv as env
import pytesseract

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

load_dotenv()

WINDOW_TITLE = env("WINDOW_TITLE", "BlueStacks")
OUTPUT_DIR = "debug_screenshots/rolls_tests"

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

def get_window():
    windows = gw.getWindowsWithTitle(WINDOW_TITLE)
    if not windows:
        print(f"❌ Finestra '{WINDOW_TITLE}' non trovata!")
        return None
    return windows[0]

def test_rolls_coordinates():
    """Prova diverse altezze verticali per trovare quella giusta."""
    print("\n" + "="*60)
    print("TEST ROLLS - TROVA COORDINATE PERFETTE")
    print("="*60)
    
    window = get_window()
    if not window:
        return
    
    screenshot = ImageGrab.grab(bbox=(window.left, window.top, window.left + window.width, window.top + window.height))
    
    # Prova diverse altezze verticali
    vertical_ranges = [
        {"name": "v1_alto", "y1": 92, "y2": 94.5},
        {"name": "v2_medio", "y1": 92.5, "y2": 95},
        {"name": "v3_basso", "y1": 93, "y2": 95.5},
        {"name": "v4_stretto", "y1": 93.5, "y2": 95},
        {"name": "v5_mini", "y1": 93.5, "y2": 94.5},
    ]
    
    # Prova diverse larghezze orizzontali
    horizontal_ranges = [
        {"name": "h1_largo", "x1": 42, "x2": 58},
        {"name": "h2_medio", "x1": 43, "x2": 57},
        {"name": "h3_stretto", "x1": 44, "x2": 56},
        {"name": "h4_centrato", "x1": 45, "x2": 55},
    ]
    
    best_results = []
    
    for h_range in horizontal_ranges:
        for v_range in vertical_ranges:
            x_percent = h_range["x1"]
            right_percent = h_range["x2"]
            y_percent = v_range["y1"]
            bottom_percent = v_range["y2"]
            
            x = int(window.width * (x_percent / 100))
            y = int(window.height * (y_percent / 100))
            right = int(window.width * (right_percent / 100))
            bottom = int(window.height * (bottom_percent / 100))
            
            region = screenshot.crop((x, y, right, bottom))
            
            # Prova threshold=100 + invert=True
            gray = cv2.cvtColor(np.array(region), cv2.COLOR_RGB2GRAY)
            
            # Scala 3x
            width = int(gray.shape[1] * 3)
            height = int(gray.shape[0] * 3)
            gray = cv2.resize(gray, (width, height), interpolation=cv2.INTER_LANCZOS4)
            
            # Threshold + invert
            _, binary = cv2.threshold(gray, 100, 255, cv2.THRESH_BINARY_INV)
            
            # Salva
            processed_pil = Image.fromarray(binary)
            filename = f"rolls_{h_range['name']}_{v_range['name']}.png"
            processed_pil.save(os.path.join(OUTPUT_DIR, filename))
            
            # OCR
            text = pytesseract.image_to_string(processed_pil, config='--psm 7 -c tessedit_char_whitelist="0123456789/"')
            text_clean = text.strip().replace(" ", "")
            
            # Verifica se è nel formato X/Y
            if "/" in text_clean:
                parts = text_clean.split("/")
                if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
                    score = len(text_clean)  # Preferisci risultati più corti (meno rumore)
                    best_results.append({
                        "text": text_clean,
                        "coords": f"({x_percent}, {y_percent}, {right_percent}, {bottom_percent})",
                        "h_range": h_range["name"],
                        "v_range": v_range["name"],
                        "score": score
                    })
                    print(f"✅ {h_range['name']}_{v_range['name']:15s} -> '{text_clean}' | coords: ({x_percent}, {y_percent}, {right_percent}, {bottom_percent})")
                else:
                    print(f"⚠️  {h_range['name']}_{v_range['name']:15s} -> '{text_clean}' (formato sbagliato)")
            else:
                if text_clean:
                    print(f"❌ {h_range['name']}_{v_range['name']:15s} -> '{text_clean}' (no slash)")
                else:
                    print(f"❌ {h_range['name']}_{v_range['name']:15s} -> (vuoto)")
    
    if best_results:
        # Ordina per score (lunghezza del testo, preferendo più brevi)
        best_results.sort(key=lambda x: x["score"])
        
        print(f"\n{'='*60}")
        print("🏆 MIGLIORI RISULTATI:")
        print(f"{'='*60}")
        for result in best_results[:5]:
            print(f"  '{result['text']}' -> {result['coords']}")
        
        winner = best_results[0]
        print(f"\n🥇 VINCITORE: '{winner['text']}'")
        print(f"   Coordinate: {winner['coords']}")
    else:
        print(f"\n❌ Nessuna combinazione ha prodotto un risultato valido nel formato X/Y")
    
    print(f"\n✓ Tutte le immagini di test sono in: {OUTPUT_DIR}")

if __name__ == "__main__":
    print("Assicurati di essere nella schermata HOME del gioco!")
    print("I rolls devono essere visibili (es: 0/50, 7/50, ecc.)")
    input("Premi ENTER per iniziare...")
    
    test_rolls_coordinates()
