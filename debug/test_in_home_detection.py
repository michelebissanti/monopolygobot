"""
Test per verificare il rilevamento dell'icona in-home
"""
import pygetwindow as gw
from pytesseract import pytesseract
from utils.ocr_utils import OCRUtils
from shared_state import shared_state
import os

pytesseract.tesseract_cmd = r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe"

print("=" * 60)
print("TEST RILEVAMENTO ICONA IN-HOME")
print("=" * 60)

# Mostra info finestra
window = shared_state.window_coords
print(f"\nCoordinate finestra da shared_state:")
print(f"  x={shared_state.window_x}, y={shared_state.window_y}")
print(f"  width={shared_state.window_width}, height={shared_state.window_height}")
print(f"  window_coords={window}")

# Verifica che il file immagine esista
in_home_icon_path = os.path.join(shared_state.current_path, "images", "in-home-icon.png")
print(f"\nPercorso icona: {in_home_icon_path}")
print(f"File esiste: {os.path.exists(in_home_icon_path)}")

# Prova a trovare l'icona
ocr_utils = OCRUtils()
in_home_icon = shared_state.load_image(in_home_icon_path)

print("\nCercando icona in-home...")
result = ocr_utils.find(in_home_icon)

if result:
    print(f"✅ ICONA TROVATA!")
    print(f"   Posizione: {result}")
else:
    print("❌ ICONA NON TROVATA!")
    print("   Verifica che il gioco sia nella schermata home")

print("\n" + "=" * 60)
