"""
debug_bank_heist.py

Script di debug per verificare il rilevamento del Bank Heist.
"""

import os
from PIL import ImageGrab, ImageDraw, ImageFont
import cv2
import numpy as np
import pygetwindow as gw
from dotenv import load_dotenv
from os import getenv as env

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

def find_bank_heist_door(screenshot, bbox):
    """Cerca la porta del Bank Heist."""
    print(f"\n{'='*60}")
    print(f"RICERCA PORTA BANK HEIST")
    print(f"{'='*60}")
    
    bh_image_path = "images/bank-heist-door.png"
    
    if not os.path.exists(bh_image_path):
        print(f"❌ ERRORE: File '{bh_image_path}' non trovato!")
        return
    
    # Carica template
    template = cv2.imread(bh_image_path)
    print(f"✓ Template Bank Heist caricato")
    print(f"  Dimensioni template: {template.shape[1]}x{template.shape[0]}")
    
    # Salva template per riferimento
    template_rgb = cv2.cvtColor(template, cv2.COLOR_BGR2RGB)
    from PIL import Image
    template_pil = Image.fromarray(template_rgb)
    template_pil.save(os.path.join(OUTPUT_DIR, "bank_heist_template.png"))
    
    # Converti screenshot
    screenshot_cv = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    
    # Template matching
    res = cv2.matchTemplate(screenshot_cv, template, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    
    print(f"\nRisultati matching:")
    print(f"  Confidence massima: {max_val:.3f}")
    print(f"  Soglia richiesta:   0.750")
    
    threshold = 0.75
    loc = np.where(res >= threshold)
    
    if loc[0].size == 0:
        print(f"\n❌ PORTA BANK HEIST NON TROVATA!")
        print(f"\n💡 POSSIBILI CAUSE:")
        print(f"  1. Non sei nella schermata dove appare il Bank Heist")
        print(f"  2. Il Bank Heist non è attivo in questo momento")
        print(f"  3. L'immagine bank-heist-door.png non corrisponde")
        
        # Salva heatmap
        heatmap = cv2.normalize(res, None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8U)
        heatmap_color = cv2.applyColorMap(heatmap, cv2.COLORMAP_JET)
        cv2.imwrite(os.path.join(OUTPUT_DIR, "bank_heist_heatmap.png"), heatmap_color)
        print(f"\n✓ Heatmap salvata: {OUTPUT_DIR}/bank_heist_heatmap.png")
        
        # Mostra le migliori corrispondenze anche se sotto soglia
        print(f"\nMigliori corrispondenze (anche se sotto soglia):")
        for i in range(min(3, len(loc[0]))):
            threshold_low = max_val * 0.6
            loc_low = np.where(res >= threshold_low)
            if loc_low[0].size > 0:
                for j, (y, x) in enumerate(zip(loc_low[0][:3], loc_low[1][:3])):
                    conf = res[y, x]
                    print(f"  {j+1}. Posizione: ({x}, {y}), Confidence: {conf:.3f}")
    else:
        print(f"\n✓ PORTA BANK HEIST TROVATA!")
        
        # Prima corrispondenza
        y, x = loc[0][0], loc[1][0]
        h, w = template.shape[:2]
        
        center_relative = (x + w // 2, y + h // 2)
        center_absolute = (
            center_relative[0] + bbox[0],
            center_relative[1] + bbox[1]
        )
        
        print(f"  Posizione (relativa): {center_relative}")
        print(f"  Posizione (assoluta): {center_absolute}")
        
        # Disegna sulla screenshot
        from PIL import Image
        result_img = screenshot.copy()
        draw = ImageDraw.Draw(result_img)
        
        # Rettangolo verde
        draw.rectangle(
            [(x, y), (x + w, y + h)],
            outline="green",
            width=5
        )
        
        # Croce rossa al centro (dove cliccherà)
        cross_size = 30
        draw.line(
            [(center_relative[0] - cross_size, center_relative[1]),
             (center_relative[0] + cross_size, center_relative[1])],
            fill="red",
            width=5
        )
        draw.line(
            [(center_relative[0], center_relative[1] - cross_size),
             (center_relative[0], center_relative[1] + cross_size)],
            fill="red",
            width=5
        )
        
        # Testo
        try:
            font = ImageFont.truetype("arial.ttf", 30)
        except:
            font = ImageFont.load_default()
        
        draw.text((x, y - 40), f"BANK HEIST! Click qui: {center_relative}", fill="green", font=font)
        
        result_path = os.path.join(OUTPUT_DIR, "bank_heist_trovato.png")
        result_img.save(result_path)
        print(f"\n✓ Risultato salvato: {result_path}")
        print(f"\n✅ Il bot dovrebbe cliccare sulla croce rossa al centro!")
        
        # Controlla corrispondenze multiple
        all_matches = list(zip(*loc[::-1]))
        if len(all_matches) > 1:
            print(f"\n⚠️  Trovate {len(all_matches)} corrispondenze!")
            for i, (mx, my) in enumerate(all_matches[:3]):
                print(f"    {i+1}. Posizione: ({mx + w//2}, {my + h//2})")

def main():
    print(f"\n{'#'*60}")
    print(f"#  DEBUG BANK HEIST - MonopolyGoBot")
    print(f"{'#'*60}")
    
    window = get_window()
    if not window:
        return
    
    print(f"\n✓ Finestra trovata: {window.title}")
    print(f"  Posizione: ({window.left}, {window.top})")
    print(f"  Dimensioni: {window.width}x{window.height}")
    
    bbox = (window.left, window.top, window.left + window.width, window.top + window.height)
    
    try:
        from PIL import Image
        screenshot = ImageGrab.grab(bbox=bbox)
        screenshot.save(os.path.join(OUTPUT_DIR, "bank_heist_screenshot.png"))
        print(f"\n✓ Screenshot salvato: {OUTPUT_DIR}/bank_heist_screenshot.png")
        
        find_bank_heist_door(screenshot, bbox)
        
        print(f"\n{'='*60}")
        print(f"DEBUG COMPLETATO!")
        print(f"{'='*60}")
        print(f"\n📁 File salvati in: {OUTPUT_DIR}/")
        print(f"\n💡 ISTRUZIONI:")
        print(f"  1. Controlla 'bank_heist_screenshot.png' - vedi la finestra catturata")
        print(f"  2. Controlla 'bank_heist_template.png' - l'immagine che cerca")
        print(f"  3. Se trovato, 'bank_heist_trovato.png' mostra dove cliccherà")
        print(f"  4. Se non trovato, 'bank_heist_heatmap.png' mostra le zone simili")
        print(f"\n")
        
    except Exception as e:
        print(f"\n❌ ERRORE: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
