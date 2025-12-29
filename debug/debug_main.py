"""
debug_main.py

Debug per verificare cosa succede quando avvii il bot dal main.
"""

import os
from time import sleep
from utils.logger import logger
from shared_state import shared_state
import pygetwindow as gw
from dotenv import load_dotenv

load_dotenv()

def monitor_game_state():
    """Monitora lo stato del gioco ogni 2 secondi."""
    print("\n" + "="*60)
    print("MONITOR STATO GIOCO")
    print("="*60)
    print("\nPremi Ctrl+C per fermare il monitor\n")
    
    try:
        iteration = 0
        while True:
            iteration += 1
            
            # Leggi stato
            rolls = shared_state.rolls
            money = shared_state.money
            in_home = shared_state.in_home_status
            builder_running = shared_state.builder_running
            autoroller_running = shared_state.autoroller_running
            
            # Stampa stato
            print(f"\n[{iteration}] Stato alle {sleep.__module__}:")
            print(f"  In Home:         {in_home}")
            print(f"  Rolls:           {rolls}")
            print(f"  Money:           {money:,}" if money else f"  Money:           {money}")
            print(f"  Builder Running: {builder_running}")
            print(f"  Auto-Roll:       {autoroller_running}")
            
            # Verifica condizioni building
            if rolls == 0 and money and money >= 1000:
                print(f"  ✅ CONDIZIONI PER BUILD SODDISFATTE!")
                if not builder_running:
                    print(f"  ⚠️  MA IL BUILDER NON È ATTIVO!")
            elif rolls == 0:
                print(f"  ⚠️  Rolls = 0 ma money insufficiente ({money if money else 'None'})")
            elif money and money >= 1000:
                print(f"  ⚠️  Money sufficiente ma rolls = {rolls}")
            
            sleep(2)
            
    except KeyboardInterrupt:
        print("\n\nMonitor fermato dall'utente")

if __name__ == "__main__":
    print("Questo script monitora lo stato del gioco")
    print("Avvia il bot con 'python main.py' in un altro terminale")
    print("Poi premi Page Up per attivare tutti gli handler")
    print("\nAssicurati che:")
    print("  - Sei nella schermata HOME")
    print("  - Hai 0 rolls")
    print("  - Hai almeno 1000 di denaro")
    
    # Inizializza window per shared_state
    WINDOW_TITLE = os.getenv("WINDOW_TITLE", "BlueStacks")
    windows = gw.getWindowsWithTitle(WINDOW_TITLE)
    if not windows:
        print(f"\n❌ Finestra '{WINDOW_TITLE}' non trovata!")
        exit(1)
    
    window = windows[0]
    shared_state.window = (window.left, window.top, window.width, window.height)
    shared_state.window_coords = (window.left, window.top, window.left + window.width, window.top + window.height)
    
    print(f"\n✓ Finestra trovata: {window.title}")
    
    input("\nPremi ENTER per iniziare il monitor...")
    
    monitor_game_state()
