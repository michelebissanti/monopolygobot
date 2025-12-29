"""
find_ocr_regions.py

Script interattivo per trovare le coordinate corrette per OCR.
Mostra lo screenshot e ti permette di selezionare manualmente le regioni.
"""

import os
from PIL import Image, ImageGrab, ImageDraw, ImageFont
import pygetwindow as gw
from dotenv import load_dotenv
from os import getenv as env
import cv2
import numpy as np

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

def create_interactive_guide():
    """Crea una guida visiva con le regioni da identificare."""
    print("\n" + "="*60)
    print("TROVA COORDINATE OCR - MonopolyGoBot")
    print("="*60)
    
    window = get_window()
    if not window:
        return
    
    print(f"✓ Finestra trovata: {window.title}")
    print(f"  Dimensioni: {window.width}x{window.height}")
    print(f"  Posizione: ({window.left}, {window.top})")
    
    # Cattura screenshot
    screenshot = ImageGrab.grab(bbox=(window.left, window.top, window.left + window.width, window.top + window.height))
    
    # Crea copia annotata
    annotated = screenshot.copy()
    draw = ImageDraw.Draw(annotated)
    
    try:
        font = ImageFont.truetype("arial.ttf", 20)
        font_small = ImageFont.truetype("arial.ttf", 14)
    except:
        font = ImageFont.load_default()
        font_small = ImageFont.load_default()
    
    # Definisci le aree da cercare
    regions = {
        "ROLLS (0/50)": {
            "search_area": (0.35, 0.85, 0.65, 0.95),  # Area dove cercare
            "color": "#FF0000",
            "description": "Cerca i rolls (es: 0/50) in questa area ROSSA"
        },
        "MULTIPLIER (x1)": {
            "search_area": (0.45, 0.65, 0.65, 0.75),  # Area dove cercare
            "color": "#00FF00",
            "description": "Cerca il moltiplicatore (es: x1) in questa area VERDE"
        },
        "MONEY": {
            "search_area": (0.30, 0.03, 0.65, 0.12),  # Area dove cercare
            "color": "#0000FF",
            "description": "Cerca i soldi in questa area BLU (già funzionante)"
        }
    }
    
    colors = {
        "#FF0000": (255, 0, 0, 128),
        "#00FF00": (0, 255, 0, 128),
        "#0000FF": (0, 0, 255, 128)
    }
    
    overlay = Image.new('RGBA', screenshot.size, (255, 255, 255, 0))
    overlay_draw = ImageDraw.Draw(overlay)
    
    for name, info in regions.items():
        x1_pct, y1_pct, x2_pct, y2_pct = info["search_area"]
        x1 = int(window.width * x1_pct)
        y1 = int(window.height * y1_pct)
        x2 = int(window.width * x2_pct)
        y2 = int(window.height * y2_pct)
        
        color = colors[info["color"]]
        
        # Disegna rettangolo semitrasparente
        overlay_draw.rectangle([x1, y1, x2, y2], fill=color, outline=info["color"], width=3)
        
        # Aggiungi etichetta
        text_y = y1 - 25 if y1 > 30 else y2 + 5
        draw.text((x1, text_y), name, fill=info["color"], font=font)
    
    # Combina overlay con screenshot
    annotated = Image.alpha_composite(annotated.convert('RGBA'), overlay).convert('RGB')
    
    # Salva
    output_path = os.path.join(OUTPUT_DIR, "find_regions_guide.png")
    annotated.save(output_path)
    
    print(f"\n✓ Guida salvata in: {output_path}")
    print("\nAPRI L'IMMAGINE e identifica visivamente:")
    print("  🔴 AREA ROSSA: Dove si trova '0/50' (rolls)?")
    print("  🟢 AREA VERDE: Dove si trova 'x1' (multiplier)?")
    print("  🔵 AREA BLU: Dove si trovano i soldi? (già funzionante)")
    
    print("\nDopo aver identificato le posizioni, usa questo tool:")
    print("  https://www.mobilefish.com/services/record_mouse_coordinates/record_mouse_coordinates.php")
    print("\nOppure usa Paint per vedere le coordinate pixel precise.")
    
    # Crea anche crop delle aree sospette per analisi dettagliata
    print("\n" + "="*60)
    print("CROP DELLE AREE SOSPETTE")
    print("="*60)
    
    crop_regions = {
        "rolls_area": (0.35, 0.85, 0.65, 0.95),
        "multiplier_area": (0.45, 0.65, 0.65, 0.75),
        "bottom_half": (0.0, 0.50, 1.0, 1.0),  # Metà inferiore completa
    }
    
    for name, (x1_pct, y1_pct, x2_pct, y2_pct) in crop_regions.items():
        x1 = int(window.width * x1_pct)
        y1 = int(window.height * y1_pct)
        x2 = int(window.width * x2_pct)
        y2 = int(window.height * y2_pct)
        
        crop = screenshot.crop((x1, y1, x2, y2))
        crop_path = os.path.join(OUTPUT_DIR, f"crop_{name}.png")
        crop.save(crop_path)
        print(f"  ✓ {crop_path}")
    
    print("\n💡 ISTRUZIONI:")
    print("1. Apri find_regions_guide.png")
    print("2. Identifica VISIVAMENTE dove sono i rolls e il multiplier")
    print("3. Apri crop_bottom_half.png per vedere meglio la parte bassa")
    print("4. Rispondi con le coordinate pixel esatte o descrivimi dove sono")

if __name__ == "__main__":
    create_interactive_guide()
