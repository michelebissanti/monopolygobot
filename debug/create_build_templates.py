"""
create_build_templates.py

Script per aiutarti a creare i template necessari per il sistema di building.
"""

import os
from PIL import ImageGrab
import pygetwindow as gw
from dotenv import load_dotenv
from os import getenv as env

load_dotenv()

WINDOW_TITLE = env("WINDOW_TITLE", "BlueStacks")
OUTPUT_DIR = "images"

def get_window():
    windows = gw.getWindowsWithTitle(WINDOW_TITLE)
    if not windows:
        print(f"❌ Finestra '{WINDOW_TITLE}' non trovata!")
        return None
    return windows[0]

def create_templates():
    """Guida l'utente nella creazione dei template necessari."""
    print("\n" + "="*60)
    print("CREAZIONE TEMPLATE PER IL SISTEMA DI BUILDING")
    print("="*60)
    
    window = get_window()
    if not window:
        return
    
    print(f"\n✓ Finestra trovata: {window.title}")
    
    # Lista dei template necessari
    templates_needed = [
        {
            "name": "build.png",
            "description": "Pulsante BUILD nella schermata home",
            "instructions": "Vai nella schermata HOME e cattura SOLO il pulsante BUILD (martello con scritta BUILD)"
        },
        {
            "name": "build-exit.png",
            "description": "Pulsante X per uscire dal menu BUILD",
            "instructions": "Entra nel menu BUILD e cattura SOLO il pulsante X in alto a sinistra per uscire"
        },
        {
            "name": "building-finished.png",
            "description": "Icona che indica che un building è al massimo livello",
            "instructions": "Nel menu BUILD, cattura l'icona che appare quando un building è completato (es: corona, stella, checkmark)"
        }
    ]
    
    print("\n📋 TEMPLATE NECESSARI:")
    for i, template in enumerate(templates_needed, 1):
        exists = os.path.exists(os.path.join(OUTPUT_DIR, template["name"]))
        status = "✅ ESISTE" if exists else "❌ MANCANTE"
        print(f"\n{i}. {template['name']} - {status}")
        print(f"   {template['description']}")
        if not exists:
            print(f"   📝 {template['instructions']}")
    
    print("\n" + "="*60)
    print("COME CREARE I TEMPLATE")
    print("="*60)
    print("""
1. Premi Win+Shift+S per aprire lo strumento di cattura
2. Seleziona l'area ESATTA del pulsante/icona
3. L'immagine viene copiata negli appunti
4. Apri Paint (Win+R, digita 'mspaint', Enter)
5. Incolla (Ctrl+V)
6. Salva come PNG nella cartella 'images' con il nome corretto
7. IMPORTANTE: L'immagine deve essere PICCOLA e PRECISA!
   - Solo il pulsante/icona, non l'area circostante
   - Deve essere sempre uguale indipendentemente dallo stato del gioco

💡 SUGGERIMENTI:
- build.png: Cattura solo l'icona del martello + scritta BUILD
- build-exit.png: Cattura solo la X in alto a sinistra nel menu
- building-finished.png: Trova un building completato e cattura l'icona
""")
    
    print("\n" + "="*60)
    print("VERIFICA TEMPLATE ESISTENTI")
    print("="*60)
    
    for template in templates_needed:
        path = os.path.join(OUTPUT_DIR, template["name"])
        if os.path.exists(path):
            from PIL import Image
            img = Image.open(path)
            print(f"\n✅ {template['name']}")
            print(f"   Dimensioni: {img.width}x{img.height} px")
            print(f"   Formato: {img.format}")
            if img.width > 200 or img.height > 200:
                print(f"   ⚠️  ATTENZIONE: Immagine troppo grande!")
                print(f"      Ricattura solo l'icona/pulsante specifico")
        else:
            print(f"\n❌ {template['name']} - NON TROVATO")
    
    print("\n" + "="*60)
    print("PROSSIMI PASSI")
    print("="*60)
    print("""
1. Crea i template mancanti seguendo le istruzioni sopra
2. Esegui 'python debug_build_button.py' per verificare il rilevamento
3. Se tutto funziona, esegui 'python main.py' e premi Page Up
""")

if __name__ == "__main__":
    create_templates()
