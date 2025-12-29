"""
debug_player_info.py

Script di debug per verificare che PlayerInfo legga correttamente i dati di gioco.
"""

import os
from PIL import ImageGrab, ImageDraw, ImageFont
import cv2
import numpy as np
import pygetwindow as gw
from dotenv import load_dotenv
from os import getenv as env
import re

load_dotenv()

WINDOW_TITLE = env("WINDOW_TITLE", "BlueStacks")
OUTPUT_DIR = "debug_screenshots"

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

def get_window():
    """Ottiene la finestra del gioco."""
    windows = gw.getWindowsWithTitle(WINDOW_TITLE)
    if not windows:
        print(f"❌ Finestra '{WINDOW_TITLE}' non trovata!")
        return None
    return windows[0]

def preprocess_image(image, threshold_value=None, invert=None, scale_factor=1):
    """Preprocessa l'immagine per OCR."""
    # Converti in grayscale
    gray = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)
    
    # Scala
    if scale_factor > 1:
        width = int(gray.shape[1] * scale_factor)
        height = int(gray.shape[0] * scale_factor)
        gray = cv2.resize(gray, (width, height), interpolation=cv2.INTER_LANCZOS4)
    
    # Threshold
    if threshold_value:
        _, gray = cv2.threshold(gray, threshold_value, 255, cv2.THRESH_BINARY)
    
    # Inverti
    if invert:
        gray = cv2.bitwise_not(gray)
    
    return gray

def test_in_home_icon(screenshot, bbox):
    """Verifica il rilevamento dell'icona in-home."""
    print(f"\n{'='*60}")
    print(f"TEST 1: IN-HOME ICON (CRITICO!)")
    print(f"{'='*60}")
    
    icon_path = "images/in-home-icon.png"
    
    if not os.path.exists(icon_path):
        print(f"❌ ERRORE: File '{icon_path}' non trovato!")
        print(f"   QUESTO È IL PROBLEMA! Senza questa icona il bot non parte.")
        return False
    
    template = cv2.imread(icon_path)
    print(f"✓ Template in-home caricato")
    
    screenshot_cv = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    res = cv2.matchTemplate(screenshot_cv, template, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    
    threshold = 0.75
    
    print(f"\nRisultato:")
    print(f"  Confidence: {max_val:.3f}")
    print(f"  Soglia:     {threshold:.3f}")
    
    if max_val >= threshold:
        print(f"\n✅ IN-HOME ICON TROVATA!")
        print(f"   Il bot SA che sei nella schermata home.")
        return True
    else:
        print(f"\n❌ IN-HOME ICON NON TROVATA!")
        print(f"\n💥 QUESTO È IL PROBLEMA PRINCIPALE!")
        print(f"   Il bot pensa che NON sei nella schermata home.")
        print(f"   Quindi NON leggerà rolls, money, multiplier.")
        print(f"   E NON attiverà autoroll, building, ecc.")
        print(f"\n💡 SOLUZIONE:")
        print(f"   1. Assicurati di essere nella schermata HOME del gioco")
        print(f"   2. L'icona in-home-icon.png deve corrispondere a un'icona sempre visibile nella home")
        print(f"   3. Rifa screenshot dell'icona se necessario")
        return False

def test_rolls_ocr(screenshot, window):
    """Testa la lettura dei rolls."""
    print(f"\n{'='*60}")
    print(f"TEST 2: LETTURA ROLLS")
    print(f"{'='*60}")
    
    x_percent, y_percent, right_percent, bottom_percent = (43, 92, 57, 94.5)
    
    x = int(window.left + (window.width * (x_percent / 100)))
    y = int(window.top + (window.height * (y_percent / 100)))
    right = int(window.left + (window.width * (right_percent / 100)))
    bottom = int(window.top + (window.height * (bottom_percent / 100)))
    
    region = screenshot.crop((x - window.left, y - window.top, right - window.left, bottom - window.top))
    
    # Preprocessa
    processed = preprocess_image(region, threshold_value=100, invert=True, scale_factor=3)
    
    from PIL import Image
    processed_pil = Image.fromarray(processed)
    processed_pil.save(os.path.join(OUTPUT_DIR, "ocr_rolls_processed.png"))
    
    # OCR
    import pytesseract
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    rolls_text = pytesseract.image_to_string(processed_pil, config='--psm 6 -c tessedit_char_whitelist="0123456789/"')
    
    print(f"  Regione: ({x_percent}%, {y_percent}%) a ({right_percent}%, {bottom_percent}%)")
    print(f"  Testo grezzo OCR: '{rolls_text.strip()}'")
    
    rolls_text_e = re.sub(r"([^0-9/])", "", rolls_text)
    rolls_parts = rolls_text_e.split("/")
    
    if len(rolls_parts) == 2:
        try:
            rolls = int(rolls_parts[0].strip())
            roll_capacity = int(rolls_parts[1].strip())
            print(f"\n✅ ROLLS LETTI: {rolls}/{roll_capacity}")
            return True
        except:
            print(f"\n❌ ERRORE nel parsing: '{rolls_parts}'")
            return False
    else:
        print(f"\n❌ Formato non valido: '{rolls_text_e}'")
        return False

def test_money_ocr(screenshot, window):
    """Testa la lettura del denaro."""
    print(f"\n{'='*60}")
    print(f"TEST 3: LETTURA MONEY")
    print(f"{'='*60}")
    
    x_percent, y_percent, right_percent, bottom_percent = (33.5, 5, 62, 9)
    
    x = int(window.left + (window.width * (x_percent / 100)))
    y = int(window.top + (window.height * (y_percent / 100)))
    right = int(window.left + (window.width * (right_percent / 100)))
    bottom = int(window.top + (window.height * (bottom_percent / 100)))
    
    region = screenshot.crop((x - window.left, y - window.top, right - window.left, bottom - window.top))
    region.save(os.path.join(OUTPUT_DIR, "ocr_money_raw.png"))
    
    # OCR
    import pytesseract
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    money_text = pytesseract.image_to_string(region)
    
    print(f"  Regione: ({x_percent}%, {y_percent}%) a ({right_percent}%, {bottom_percent}%)")
    print(f"  Testo grezzo OCR: '{money_text.strip()}'")
    
    money_text = "".join(filter(str.isdigit, money_text))
    
    if money_text.isdigit():
        print(f"\n✅ MONEY LETTO: {int(money_text):,}")
        return True
    else:
        print(f"\n❌ Non è un numero valido: '{money_text}'")
        return False

def test_multiplier_ocr(screenshot, window):
    """Testa la lettura del moltiplicatore."""
    print(f"\n{'='*60}")
    print(f"TEST 4: LETTURA MULTIPLIER")
    print(f"{'='*60}")
    
    x_percent, y_percent, right_percent, bottom_percent = (53, 70, 57, 73)
    
    x = int(window.left + (window.width * (x_percent / 100)))
    y = int(window.top + (window.height * (y_percent / 100)))
    right = int(window.left + (window.width * (right_percent / 100)))
    bottom = int(window.top + (window.height * (bottom_percent / 100)))
    
    region = screenshot.crop((x - window.left, y - window.top, right - window.left, bottom - window.top))
    
    # Preprocessa (grayscale_only funziona perfetto)
    processed = preprocess_image(region, threshold_value=None, invert=False, scale_factor=3)
    
    from PIL import Image
    processed_pil = Image.fromarray(processed)
    processed_pil.save(os.path.join(OUTPUT_DIR, "ocr_multiplier_processed.png"))
    
    # OCR
    import pytesseract
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    multiplier_text = pytesseract.image_to_string(processed_pil, config='--psm 7 --oem 3 -c tessedit_char_whitelist=x0123456789')
    
    print(f"  Regione: ({x_percent}%, {y_percent}%) a ({right_percent}%, {bottom_percent}%)")
    print(f"  Testo grezzo OCR: '{multiplier_text.strip()}'")
    
    multiplier_text = "".join(filter(str.isdigit, multiplier_text))
    
    if multiplier_text.isdigit():
        print(f"\n✅ MULTIPLIER LETTO: x{int(multiplier_text)}")
        return True
    else:
        print(f"\n❌ Non è un numero valido: '{multiplier_text}'")
        return False

def main():
    print(f"\n{'#'*60}")
    print(f"#  DEBUG PLAYER INFO - MonopolyGoBot")
    print(f"#  Verifica lettura dati di gioco")
    print(f"{'#'*60}")
    
    print(f"\n⚠️  ASSICURATI DI ESSERE NELLA SCHERMATA HOME DEL GIOCO!")
    input("Premi ENTER quando sei pronto...")
    
    window = get_window()
    if not window:
        return
    
    print(f"\n✓ Finestra trovata: {window.title}")
    
    bbox = (window.left, window.top, window.left + window.width, window.top + window.height)
    
    try:
        from PIL import Image
        screenshot = ImageGrab.grab(bbox=bbox)
        screenshot.save(os.path.join(OUTPUT_DIR, "playerinfo_screenshot.png"))
        
        # Test 1: In-home icon (CRITICO!)
        in_home_ok = test_in_home_icon(screenshot, bbox)
        
        if in_home_ok:
            # Test 2-4: Solo se in-home è OK
            test_rolls_ocr(screenshot, window)
            test_money_ocr(screenshot, window)
            test_multiplier_ocr(screenshot, window)
        else:
            print(f"\n⚠️  Salto test OCR perché in-home non funziona")
        
        print(f"\n{'='*60}")
        print(f"RIEPILOGO")
        print(f"{'='*60}")
        
        if in_home_ok:
            print(f"✅ Il bot dovrebbe funzionare!")
            print(f"\n📁 Controlla le immagini in {OUTPUT_DIR}/ per verificare l'OCR")
        else:
            print(f"❌ IL BOT NON FUNZIONERÀ!")
            print(f"\n🔧 COSA FARE:")
            print(f"   1. Vai alla schermata HOME del gioco")
            print(f"   2. Trova un'icona SEMPRE visibile (es. icona menu, settings, ecc.)")
            print(f"   3. Fai screenshot SOLO di quell'icona")
            print(f"   4. Salvala come images/in-home-icon.png")
            print(f"   5. Riprova questo script")
        
        print(f"\n")
        
    except Exception as e:
        print(f"\n❌ ERRORE: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
