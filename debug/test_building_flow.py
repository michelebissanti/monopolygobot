"""
test_building_flow.py

Test completo del flusso di building per verificare che tutto funzioni.
"""

import os
import sys
from time import sleep
from dotenv import load_dotenv

# Aggiungi il path corrente
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

load_dotenv()

from utils.logger import logger
from shared_state import shared_state
from utils.player_info import PlayerInfo
import pygetwindow as gw

def test_building_flow():
    """Testa il flusso completo di building."""
    print("\n" + "="*60)
    print("TEST FLUSSO BUILDING - MonopolyGoBot")
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
    
    print(f"✓ Finestra trovata: {window.title}")
    print(f"  Dimensioni: {window.width}x{window.height}")
    
    # Inizializza PlayerInfo per leggere rolls e money
    print("\n1. Inizializzazione PlayerInfo...")
    player_info = PlayerInfo()
    player_info.run()
    
    print("   Attendo lettura dati di gioco...")
    sleep(3)
    
    # Leggi stato corrente
    with shared_state.rolls_condition:
        shared_state.rolls_condition.wait()
        rolls = shared_state.rolls
    
    with shared_state.money_condition:
        shared_state.money_condition.wait()
        money = shared_state.money
    
    with shared_state.in_home_condition:
        shared_state.in_home_condition.wait()
        in_home = shared_state.in_home_status
    
    print(f"\n2. Stato attuale del gioco:")
    print(f"   In home: {in_home}")
    print(f"   Rolls: {rolls}")
    print(f"   Money: {money:,}")
    
    if not in_home:
        print("\n❌ ERRORE: Non sei nella schermata home!")
        print("   Assicurati di essere nella schermata principale del gioco")
        return
    
    # Verifica condizioni per building
    print(f"\n3. Verifica condizioni per building:")
    print(f"   Rolls == 0? {rolls == 0}")
    print(f"   Money >= 1000? {money >= 1000}")
    
    if rolls == 0 and money >= 1000:
        print("\n✅ CONDIZIONI SODDISFATTE - Il building dovrebbe attivarsi!")
    else:
        print("\n⚠️  CONDIZIONI NON SODDISFATTE")
        if rolls > 0:
            print(f"   Hai ancora {rolls} rolls disponibili")
            print(f"   Il building si attiva SOLO quando rolls == 0")
        if money < 1000:
            print(f"   Hai solo {money} di denaro")
            print(f"   Serve almeno 1000 per costruire")
        return
    
    # Test manuale del building_handler
    print(f"\n4. Test del BuildingHandler...")
    print(f"   Importo BuildingHandler...")
    
    from handlers.building_handler import BuildingHandler
    
    print(f"   Creo istanza...")
    builder = BuildingHandler()
    
    print(f"\n5. Test enter_build_menu()...")
    print(f"   Verifica se sei già nel menu...")
    
    in_menu = builder.check_menu_status()
    print(f"   Sei nel menu BUILD? {in_menu}")
    
    if not in_menu:
        print(f"\n   Tentativo di entrare nel menu BUILD...")
        builder.enter_build_menu()
        sleep(2)
        in_menu = builder.check_menu_status()
        print(f"   Sei entrato nel menu? {in_menu}")
        
        if in_menu:
            print(f"\n✅ SUCCESSO! Sei nel menu BUILD")
        else:
            print(f"\n❌ FALLITO! Non sono riuscito ad entrare nel menu")
            print(f"\n💡 POSSIBILI CAUSE:")
            print(f"   1. Il pulsante BUILD non viene trovato correttamente")
            print(f"   2. Il click non funziona")
            print(f"   3. Il template build-exit.png non corrisponde")
            return
    else:
        print(f"\n✅ Sei già nel menu BUILD")
    
    print(f"\n6. Test gather_board_name()...")
    board_name = builder.gather_board_name()
    print(f"   Board name: {board_name}")
    
    if board_name and board_name != "":
        print(f"\n✅ Board name letto correttamente!")
    else:
        print(f"\n⚠️  Board name non letto (potrebbe essere normale)")
    
    print(f"\n" + "="*60)
    print("TEST COMPLETATO")
    print("="*60)
    print(f"""
RIEPILOGO:
- PlayerInfo: ✓ Funzionante
- Condizioni building: {"✓ Soddisfatte" if rolls == 0 and money >= 1000 else "✗ Non soddisfatte"}
- Accesso al menu BUILD: {"✓ Funzionante" if in_menu else "✗ Non funzionante"}

PROSSIMI PASSI:
1. Se tutto funziona, esegui 'python main.py' e premi Page Up
2. Il bot dovrebbe automaticamente entrare in modalità build quando rolls == 0
3. Controlla i log in log.txt per vedere cosa succede
""")

if __name__ == "__main__":
    print("ASSICURATI DI ESSERE NELLA SCHERMATA HOME DEL GIOCO")
    print("(non nel menu BUILD)")
    print("Rolls dovrebbero essere a 0 e avere almeno 1000 di denaro")
    input("\nPremi ENTER per iniziare il test...")
    
    try:
        test_building_flow()
    except KeyboardInterrupt:
        print("\n\nTest interrotto dall'utente")
    except Exception as e:
        print(f"\n\n❌ ERRORE durante il test:")
        print(f"   {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
