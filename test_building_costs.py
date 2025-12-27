"""
Test per verificare la lettura dei costi degli edifici dalla schermata build
"""
from pytesseract import pytesseract
from shared_state import shared_state
from utils.ocr_utils import OCRUtils
from utils.logger import logger
import time
import re

pytesseract.tesseract_cmd = r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe"

print("=" * 60)
print("TEST LETTURA COSTI EDIFICI")
print("=" * 60)
print("\nASSICURATI DI ESSERE NELLA SCHERMATA BUILD!")
print("(Quella dove vedi i 3-5 edifici con i loro livelli di upgrade)")
input("\nPremi ENTER quando sei pronto...")

print("\nInfo finestra:")
print(f"  x={shared_state.window_x}, y={shared_state.window_y}")
print(f"  width={shared_state.window_width}, height={shared_state.window_height}")

# Definisci gli edifici da testare (stessa struttura di BuildingHandler)
buildings = [
    {
        "name": "building1",
        "x_percent": 37,
        "y_percent": 86,
        "right_percent": 40.5,
        "bottom_percent": 91,
    },
    {
        "name": "building2",
        "x_percent": 42.5,
        "y_percent": 86,
        "right_percent": 46,
        "bottom_percent": 91,
    },
    {
        "name": "building3",
        "x_percent": 48.5,
        "y_percent": 86,
        "right_percent": 52,
        "bottom_percent": 91,
    },
    {
        "name": "building4",
        "x_percent": 54.5,
        "y_percent": 86,
        "right_percent": 58,
        "bottom_percent": 91,
    },
    {
        "name": "building5",
        "x_percent": 60.5,
        "y_percent": 86,
        "right_percent": 64,
        "bottom_percent": 91,
    },
]

def extract_and_convert_cost(cost_text):
    """Estrae e converte i costi dagli OCR results"""
    print(f"    Parsing: '{cost_text}'")
    pattern = r"(\d+(\.\d+)?)([MK]?)"
    match = re.search(pattern, cost_text)
    if match:
        numeric_part, decimal_part, unit_part = match.groups()
        if not unit_part and decimal_part:
            conversion_factor = 1000
        else:
            conversion_factor = (
                1_000_000 if unit_part == "M" else (1_000 if unit_part == "K" else 1)
            )
        numeric_part = numeric_part.replace(",", "")
        cost_value = int(float(numeric_part) * conversion_factor)
        return cost_value
    else:
        return 0

print("\n" + "=" * 60)
print("LETTURA COSTI (le immagini verranno salvate)")
print("=" * 60)

ocr_utils = OCRUtils()

# Testa la lettura dei costi per ogni edificio
for building_info in buildings:
    building_name = building_info["name"]
    x_percent = building_info["x_percent"]
    y_percent = building_info["y_percent"]
    right_percent = building_info["right_percent"]
    bottom_percent = building_info["bottom_percent"]
    
    print(f"\n{building_name}:")
    print(f"  Coordinate OCR: x={x_percent}%, y={y_percent}%, right={right_percent}%, bottom={bottom_percent}%")
    
    ocr_settings = r"--psm 7 --oem 3 -c tessedit_char_whitelist=0123456789.MK"
    process_settings = {
        "threshold_value": 100,
        "invert": True,
        "scale_factor": 3,
    }
    
    cost_text = ocr_utils.ocr_to_str(
        x_percent,
        y_percent,
        right_percent,
        bottom_percent,
        output_image_path=f"test_cost_{building_name}.png",
        ocr_settings=ocr_settings,
        process_settings=process_settings,
    )
    
    print(f"  OCR raw text: '{cost_text}'")
    
    cost = extract_and_convert_cost(cost_text)
    print(f"  Costo convertito: {cost:,}")
    print(f"  ✓ Immagine salvata: test_cost_{building_name}.png")

print("\n" + "=" * 60)
print("Test completato! Controlla le immagini salvate.")
print("=" * 60)
