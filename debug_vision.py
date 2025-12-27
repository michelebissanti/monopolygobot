"""
debug_vision.py

Script di debug per visualizzare cosa vede il bot.
Mostra la finestra rilevata, gli screenshot e la ricerca delle immagini.
"""

import os
import sys
from PIL import ImageGrab, ImageDraw, ImageFont
import cv2
import numpy as np
import pygetwindow as gw
from dotenv import load_dotenv
from os import getenv as env

load_dotenv()

# Configurazione
WINDOW_TITLE = env("WINDOW_TITLE", "BlueStacks")
OUTPUT_DIR = "debug_screenshots"

# Crea la directory per gli screenshot se non esiste
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

def get_window_info():
    """Ottiene informazioni sulla finestra del gioco."""
    print(f"\n{'='*60}")
    print(f"RICERCA FINESTRA: '{WINDOW_TITLE}'")
    print(f"{'='*60}")
    
    windows = gw.getWindowsWithTitle(WINDOW_TITLE)
    
    if not windows:
        print(f"❌ ERRORE: Nessuna finestra trovata con il titolo '{WINDOW_TITLE}'")
        print("\nFinestre disponibili:")
        all_windows = gw.getAllWindows()
        for i, win in enumerate(all_windows[:10]):  # Mostra solo le prime 10
            print(f"  {i+1}. {win.title}")
        return None
    
    window = windows[0]
    
    print(f"✓ Finestra trovata!")
    print(f"\nCoordinate finestra:")
    print(f"  Left (X):    {window.left}")
    print(f"  Top (Y):     {window.top}")
    print(f"  Width:       {window.width}")
    print(f"  Height:      {window.height}")
    print(f"  Right:       {window.left + window.width}")
    print(f"  Bottom:      {window.top + window.height}")
    
    # Info su monitor multipli
    print(f"\n⚠️  CON DUE MONITOR:")
    if window.left < 0 or window.top < 0:
        print(f"  ⚠️  ATTENZIONE: La finestra ha coordinate negative!")
        print(f"  ⚠️  Questo può causare problemi con l'OCR.")
        print(f"  💡 SOLUZIONE: Sposta la finestra sul monitor primario")
    else:
        print(f"  ✓ Coordinate positive, dovrebbe funzionare correttamente")
    
    return window

def capture_and_save_screenshot(window):
    """Cattura uno screenshot della finestra e lo salva."""
    print(f"\n{'='*60}")
    print(f"CATTURA SCREENSHOT")
    print(f"{'='*60}")
    
    bbox = (
        window.left,
        window.top,
        window.left + window.width,
        window.top + window.height
    )
    
    try:
        screenshot = ImageGrab.grab(bbox=bbox)
        
        # Salva screenshot originale
        original_path = os.path.join(OUTPUT_DIR, "1_finestra_completa.png")
        screenshot.save(original_path)
        print(f"✓ Screenshot salvato: {original_path}")
        print(f"  Dimensioni: {screenshot.size}")
        
        # Crea una versione annotata con le coordinate
        annotated = screenshot.copy()
        draw = ImageDraw.Draw(annotated)
        
        # Aggiungi testo con le coordinate
        try:
            font = ImageFont.truetype("arial.ttf", 40)
        except:
            font = ImageFont.load_default()
        
        text = f"Window: {window.left}, {window.top}\nSize: {window.width}x{window.height}"
        draw.text((10, 10), text, fill="red", font=font)
        
        # Disegna un rettangolo rosso ai bordi per verificare l'area catturata
        draw.rectangle([(5, 5), (screenshot.width-5, screenshot.height-5)], outline="red", width=5)
        
        annotated_path = os.path.join(OUTPUT_DIR, "2_finestra_annotata.png")
        annotated.save(annotated_path)
        print(f"✓ Screenshot annotato salvato: {annotated_path}")
        
        return screenshot, bbox
        
    except Exception as e:
        print(f"❌ ERRORE durante la cattura: {e}")
        return None, None

def find_go_button(screenshot, bbox):
    """Cerca il pulsante GO nell'immagine."""
    print(f"\n{'='*60}")
    print(f"RICERCA PULSANTE GO")
    print(f"{'='*60}")
    
    go_image_path = "images/go.png"
    
    if not os.path.exists(go_image_path):
        print(f"❌ ERRORE: File '{go_image_path}' non trovato!")
        return
    
    # Carica l'immagine template
    template = cv2.imread(go_image_path)
    print(f"✓ Template GO caricato: {go_image_path}")
    print(f"  Dimensioni template: {template.shape[1]}x{template.shape[0]}")
    
    # Salva il template per riferimento
    template_rgb = cv2.cvtColor(template, cv2.COLOR_BGR2RGB)
    template_pil = Image.fromarray(template_rgb)
    template_pil.save(os.path.join(OUTPUT_DIR, "3_template_go.png"))
    
    # Converti screenshot in formato OpenCV
    screenshot_cv = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    
    # Esegui template matching
    res = cv2.matchTemplate(screenshot_cv, template, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    
    print(f"\nRisultati matching:")
    print(f"  Confidence massima: {max_val:.3f}")
    print(f"  Soglia richiesta:   0.750")
    
    threshold = 0.75
    loc = np.where(res >= threshold)
    
    if loc[0].size == 0:
        print(f"\n❌ PULSANTE GO NON TROVATO!")
        print(f"\n💡 POSSIBILI CAUSE:")
        print(f"  1. La finestra non è nella schermata home")
        print(f"  2. L'immagine go.png non corrisponde al pulsante nel gioco")
        print(f"  3. La risoluzione della finestra è diversa")
        print(f"  4. Problemi con coordinate su multi-monitor")
        
        # Salva heatmap per analisi
        heatmap = cv2.normalize(res, None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8U)
        heatmap_color = cv2.applyColorMap(heatmap, cv2.COLORMAP_JET)
        cv2.imwrite(os.path.join(OUTPUT_DIR, "4_heatmap_matching.png"), heatmap_color)
        print(f"\n✓ Heatmap salvata: debug_screenshots/4_heatmap_matching.png")
        print(f"  (Le zone rosse indicano maggiore somiglianza)")
        
    else:
        print(f"\n✓ PULSANTE GO TROVATO!")
        
        # Prendi la prima corrispondenza
        y, x = loc[0][0], loc[1][0]
        h, w = template.shape[:2]
        
        # Calcola coordinate relative e assolute
        center_relative = (x + w // 2, y + h // 2)
        center_absolute = (
            center_relative[0] + bbox[0],
            center_relative[1] + bbox[1]
        )
        
        print(f"  Posizione (relativa alla finestra): {center_relative}")
        print(f"  Posizione (assoluta sullo schermo): {center_absolute}")
        
        # Disegna rettangolo sulla posizione trovata
        result_img = screenshot.copy()
        draw = ImageDraw.Draw(result_img)
        
        # Rettangolo verde
        draw.rectangle(
            [(x, y), (x + w, y + h)],
            outline="green",
            width=5
        )
        
        # Croce rossa al centro
        cross_size = 20
        draw.line(
            [(center_relative[0] - cross_size, center_relative[1]),
             (center_relative[0] + cross_size, center_relative[1])],
            fill="red",
            width=3
        )
        draw.line(
            [(center_relative[0], center_relative[1] - cross_size),
             (center_relative[0], center_relative[1] + cross_size)],
            fill="red",
            width=3
        )
        
        # Aggiungi testo
        try:
            font = ImageFont.truetype("arial.ttf", 30)
        except:
            font = ImageFont.load_default()
        
        draw.text((x, y - 40), f"GO TROVATO! Click qui: {center_relative}", fill="green", font=font)
        
        result_path = os.path.join(OUTPUT_DIR, "5_go_button_trovato.png")
        result_img.save(result_path)
        print(f"\n✓ Risultato salvato: {result_path}")
        print(f"\n✅ Il bot CLICCHERÀ sulla croce rossa (coordinate assolute: {center_absolute})")
        
        # Mostra tutte le corrispondenze se ce ne sono multiple
        all_matches = list(zip(*loc[::-1]))
        if len(all_matches) > 1:
            print(f"\n⚠️  Trovate {len(all_matches)} corrispondenze multiple!")
            for i, (mx, my) in enumerate(all_matches[:5]):
                print(f"    {i+1}. Posizione: ({mx + w//2}, {my + h//2})")

def check_other_images(screenshot):
    """Controlla altre immagini importanti."""
    print(f"\n{'='*60}")
    print(f"VERIFICA ALTRE IMMAGINI")
    print(f"{'='*60}")
    
    important_images = [
        "images/autoroll.png",
        "images/build.png",
        "images/in-home-icon.png"
    ]
    
    screenshot_cv = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    
    for img_path in important_images:
        if os.path.exists(img_path):
            template = cv2.imread(img_path)
            res = cv2.matchTemplate(screenshot_cv, template, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
            
            status = "✓ TROVATA" if max_val >= 0.75 else "✗ Non trovata"
            print(f"  {os.path.basename(img_path):20s} - {status} (confidence: {max_val:.3f})")

def main():
    """Funzione principale."""
    print(f"\n{'#'*60}")
    print(f"#  DEBUG VISION - MonopolyGoBot")
    print(f"#  Verifica cosa vede lo script")
    print(f"{'#'*60}")
    
    # 1. Ottieni info finestra
    window = get_window_info()
    if not window:
        return
    
    # 2. Cattura screenshot
    screenshot, bbox = capture_and_save_screenshot(window)
    if not screenshot:
        return
    
    # 3. Cerca pulsante GO
    find_go_button(screenshot, bbox)
    
    # 4. Verifica altre immagini
    check_other_images(screenshot)
    
    print(f"\n{'='*60}")
    print(f"DEBUG COMPLETATO!")
    print(f"{'='*60}")
    print(f"\n📁 Tutti i file sono stati salvati in: {OUTPUT_DIR}/")
    print(f"\n💡 PROSSIMI PASSI:")
    print(f"  1. Apri la cartella '{OUTPUT_DIR}' e controlla le immagini")
    print(f"  2. Verifica che la finestra catturata sia corretta")
    print(f"  3. Se GO non è trovato, controlla se l'immagine corrisponde")
    print(f"  4. Se hai coordinate negative, sposta la finestra sul monitor primario")
    print(f"\n")

if __name__ == "__main__":
    from PIL import Image  # Import qui per evitare conflitti
    main()
