"""
test_playerinfo_live.py

Test live per vedere se PlayerInfo scrive in shared_state.
"""

import os
import sys
from time import sleep
from dotenv import load_dotenv
import pygetwindow as gw

# Aggiungi il path corrente
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

load_dotenv()

from shared_state import shared_state
from utils.player_info import PlayerInfo
from utils.logger import logger

def test_playerinfo_live():
    """Testa PlayerInfo in tempo reale."""
    print("\n" + "="*60)
    print("TEST PLAYERINFO LIVE")
    print("="*60)
    
    # Inizializza window
    WINDOW_TITLE = os.getenv("WINDOW_TITLE", "BlueStacks")
    windows = gw.getWindowsWithTitle(WINDOW_TITLE)
    if not windows:
        print(f"❌ Finestra '{WINDOW_TITLE}' non trovata!")
        return
    
    window = windows[0]
    shared_state.window = (window.left, window.top, window.width, window.height)
    shared_state.window_coords = (window.left, window.top, window.left + window.width, window.top + window.height)
    shared_state.current_path = os.getcwd()
    shared_state.WINDOW_TITLE = WINDOW_TITLE
    
    print(f"✓ Finestra trovata: {window.title}")
    print(f"  Dimensioni: {window.width}x{window.height}")
    
    # Crea istanza PlayerInfo
    print("\n1. Creazione istanza PlayerInfo...")
    player_info = PlayerInfo()
    
    # Valori iniziali
    print(f"\n2. Valori iniziali in shared_state:")
    print(f"   rolls: {shared_state.rolls}")
    print(f"   money: {shared_state.money}")
    print(f"   multiplier: {shared_state.multiplier}")
    print(f"   in_home_status: {shared_state.in_home_status}")
    
    # Avvia i thread
    print(f"\n3. Avvio thread PlayerInfo...")
    player_info.run()
    
    print(f"\n4. Attendo 5 secondi per la lettura dati...")
    sleep(5)
    
    # Leggi i valori
    print(f"\n5. Valori dopo 5 secondi:")
    print(f"   rolls: {shared_state.rolls}")
    print(f"   money: {shared_state.money}")
    print(f"   multiplier: {shared_state.multiplier}")
    print(f"   in_home_status: {shared_state.in_home_status}")
    
    # Monitor continuo
    print(f"\n6. Monitor continuo (Ctrl+C per fermare):")
    try:
        count = 0
        while True:
            count += 1
            sleep(2)
            print(f"\n[{count}] Stato corrente:")
            print(f"    In Home:    {shared_state.in_home_status}")
            print(f"    Rolls:      {shared_state.rolls}")
            print(f"    Money:      {shared_state.money:,}" if shared_state.money else f"    Money:      {shared_state.money}")
            print(f"    Multiplier: {shared_state.multiplier}")
            
            # Verifica
            if shared_state.money and shared_state.money > 0:
                print(f"    ✅ Money viene scritto correttamente!")
            else:
                print(f"    ❌ Money è {shared_state.money}!")
                
    except KeyboardInterrupt:
        print("\n\nTest interrotto")

if __name__ == "__main__":
    print("ASSICURATI DI ESSERE NELLA SCHERMATA HOME DEL GIOCO")
    input("\nPremi ENTER per iniziare il test...")
    
    try:
        test_playerinfo_live()
    except Exception as e:
        print(f"\n❌ ERRORE: {e}")
        import traceback
        traceback.print_exc()
