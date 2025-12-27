"""
debug_build_button.py

Debug per verificare se il pulsante BUILD viene rilevato correttamente.
"""

import os
from PIL import ImageGrab, ImageDraw
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
    windows = gw.getWindowsWithTitle(WINDOW_TITLE)
    if not windows:
        print(f"❌ Finestra '{WINDOW_TITLE}' non trovata!")
        return None
    return windows[0]

def test_build_button():
    """Testa il rilevamento del pulsante BUILD."""
    print("\n" + "="*60)
    print("TEST PULSANTE BUILD")
    print("="*60)
    
    window = get_window()
    if not window:
        return
    
    print(f"✓ Finestra trovata: {window.title}")
    
    # Cattura screenshot
    screenshot = ImageGrab.grab(bbox=(window.left, window.top, window.left + window.width, window.top + window.height))
    screenshot.save(os.path.join(OUTPUT_DIR, "build_screenshot.png"))
    print(f"✓ Screenshot salvato")
    
    # Carica template
    build_template_path = "images/build.png"
    if not os.path.exists(build_template_path):
        print(f"❌ ERRORE: Template '{build_template_path}' non trovato!")
        print(f"   Devi creare questo file con un'immagine del pulsante BUILD")
        return
    
    template = cv2.imread(build_template_path)
    print(f"✓ Template BUILD caricato: {template.shape}")
    
    # Salva il template per verifica
    cv2.imwrite(os.path.join(OUTPUT_DIR, "build_template.png"), template)
    
    # Converti screenshot
    screenshot_cv = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    
    # Template matching
    res = cv2.matchTemplate(screenshot_cv, template, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    
    threshold = 0.75
    
    print(f"\nRisultato matching:")
    print(f"  Confidence: {max_val:.3f}")
    print(f"  Soglia:     {threshold:.3f}")
    print(f"  Posizione:  {max_loc}")
    
    # Disegna il risultato
    annotated = screenshot.copy()
    draw = ImageDraw.Draw(annotated)
    
    if max_val >= threshold:
        # Trovato!
        h, w = template.shape[:2]
        top_left = max_loc
        bottom_right = (top_left[0] + w, top_left[1] + h)
        center = (top_left[0] + w // 2, top_left[1] + h // 2)
        
        # Disegna rettangolo verde
        draw.rectangle([top_left, bottom_right], outline="green", width=3)
        
        # Disegna punto centrale
        r = 5
        draw.ellipse([center[0]-r, center[1]-r, center[0]+r, center[1]+r], fill="red", outline="red")
        
        # Coordinate assolute (schermo)
        abs_x = window.left + center[0]
        abs_y = window.top + center[1]
        
        print(f"\n✅ PULSANTE BUILD TROVATO!")
        print(f"   Centro: ({center[0]}, {center[1]}) relativo alla finestra")
        print(f"   Assoluto: ({abs_x}, {abs_y}) coordinate schermo")
        
        annotated.save(os.path.join(OUTPUT_DIR, "build_trovato.png"))
        print(f"\n✓ Immagine annotata salvata: build_trovato.png")
        
        return True
    else:
        print(f"\n❌ PULSANTE BUILD NON TROVATO!")
        print(f"   Confidence troppo bassa: {max_val:.3f} < {threshold:.3f}")
        print(f"\n💡 POSSIBILI CAUSE:")
        print(f"   1. L'immagine build.png non corrisponde al pulsante nel gioco")
        print(f"   2. Il pulsante BUILD non è visibile (sei già nel menu?)")
        print(f"   3. Il pulsante ha un aspetto diverso (tema/risoluzione)")
        print(f"\n💡 SOLUZIONE:")
        print(f"   1. Assicurati di essere nella schermata HOME (non nel menu BUILD)")
        print(f"   2. Cattura nuovo screenshot del pulsante BUILD con Win+Shift+S")
        print(f"   3. Salva come images/build.png")
        
        # Mostra le migliori corrispondenze
        print(f"\n   Migliori match trovati:")
        loc = np.where(res >= 0.5)  # Soglia più bassa per debug
        if loc[0].size > 0:
            for i, (y, x) in enumerate(zip(loc[0], loc[1])):
                if i >= 5:  # Max 5 risultati
                    break
                conf = res[y, x]
                print(f"   - Posizione ({x}, {y}): confidence {conf:.3f}")
                
                # Disegna rettangolo giallo per debug
                h, w = template.shape[:2]
                top_left = (x, y)
                bottom_right = (x + w, y + h)
                draw.rectangle([top_left, bottom_right], outline="yellow", width=2)
        else:
            print(f"   Nessun match trovato nemmeno con soglia 0.5")
        
        annotated.save(os.path.join(OUTPUT_DIR, "build_non_trovato.png"))
        print(f"\n✓ Immagine annotata salvata: build_non_trovato.png")
        
        return False

def test_build_menu_status():
    """Testa il rilevamento dello stato del menu BUILD."""
    print("\n" + "="*60)
    print("TEST STATO MENU BUILD")
    print("="*60)
    
    window = get_window()
    if not window:
        return
    
    # Cattura screenshot
    screenshot = ImageGrab.grab(bbox=(window.left, window.top, window.left + window.width, window.top + window.height))
    
    # Carica template del menu
    build_menu_template_path = "images/in-build-menu.png"
    if not os.path.exists(build_menu_template_path):
        print(f"❌ ERRORE: Template '{build_menu_template_path}' non trovato!")
        print(f"   Questo file è necessario per rilevare se sei nel menu BUILD")
        return
    
    template = cv2.imread(build_menu_template_path)
    print(f"✓ Template menu BUILD caricato: {template.shape}")
    
    # Template matching
    screenshot_cv = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    res = cv2.matchTemplate(screenshot_cv, template, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    
    threshold = 0.75
    
    print(f"\nRisultato matching:")
    print(f"  Confidence: {max_val:.3f}")
    print(f"  Soglia:     {threshold:.3f}")
    
    if max_val >= threshold:
        print(f"\n✅ SEI NEL MENU BUILD")
    else:
        print(f"\n✅ NON SEI NEL MENU BUILD (sei nella home)")

if __name__ == "__main__":
    print("ASSICURATI DI ESSERE NELLA SCHERMATA HOME DEL GIOCO")
    print("(non nel menu BUILD)")
    input("Premi ENTER per testare il pulsante BUILD...")
    
    build_found = test_build_button()
    
    print("\n" + "="*60)
    input("Ora ENTRA NEL MENU BUILD e premi ENTER per testare il rilevamento...")
    
    test_build_menu_status()
    
    print("\n" + "="*60)
    print("RIEPILOGO")
    print("="*60)
    print(f"Controlla le immagini in {OUTPUT_DIR}/")
    print("- build_screenshot.png = screenshot completo")
    print("- build_template.png = template usato per il matching")
    print("- build_trovato.png o build_non_trovato.png = risultato")
