from sys import exit
import sys
from utils.logger import logger, configure_logger
from shared_state import shared_state
from handlers.state_handler import StateHandler
from utils.set_console_title import SetConsoleTitle
from utils.player_info import PlayerInfo
from pytesseract import pytesseract
from time import sleep
from pynput import keyboard
import os

# Initialize logger based on window title before anything else
configure_logger(shared_state.WINDOW_TITLE)

# Set up tesseract
pytesseract.tesseract_cmd = r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
# Initialize class instances
player_info = PlayerInfo()
set_console_title = SetConsoleTitle()
state_handler = StateHandler(player_info, set_console_title)


def on_key_press(key):
    if key == keyboard.Key.f1:
        print("[STATUS] Toggling autoroll...")
        logger.info("[STATUS] Toggling autoroll...")
        sleep(0.2)
        state_handler.toggle_autoroll_handler()
        sleep(0.2)

    elif key == keyboard.Key.f2:
        print("[STATUS] Toggling bank heist handler...")
        logger.info("[STATUS] Toggling bank heist handler...")
        sleep(0.2)
        state_handler.toggle_bank_heist_handler()
        sleep(0.2)

    elif key == keyboard.Key.f3:
        print("[STATUS] Toggling shut down handler...")
        logger.info("[STATUS] Toggling shut down handler...")
        sleep(0.2)
        state_handler.toggle_shut_down_handler()
        sleep(0.2)

    elif key == keyboard.Key.f4:
        print("[STATUS] Toggling UI handler...")
        logger.info("[STATUS] Toggling UI handler...")
        sleep(0.2)
        state_handler.toggle_ui_handler()
        sleep(0.2)

    elif key == keyboard.Key.f5:
        print("[STATUS] Toggling building monitor...")
        logger.info("[STATUS] Toggling building monitor...")
        sleep(0.2)
        state_handler.toggle_building_monitor()
        sleep(0.2)

    elif key == keyboard.Key.f6:
        print("[STATUS] Toggling multiplier monitor...")
        logger.info("[STATUS] Toggling multiplier monitor...")
        sleep(0.2)
        state_handler.toggle_multiplier_monitor()
        sleep(0.2)

    elif key == keyboard.Key.f7:
        print("[STATUS] Toggling autoroll monitor...")
        logger.info("[STATUS] Toggling autoroll monitor...")
        sleep(0.2)
        state_handler.toggle_autoroll_monitor()
        sleep(0.2)

    elif key == keyboard.Key.f8:
        print("[STATUS] Toggling destruction handler...")
        logger.info("[STATUS] Toggling destruction handler...")
        sleep(0.2)
        state_handler.toggle_destruction_handler()
        sleep(0.2)

    elif key == keyboard.Key.page_up:
        print("[STATUS] Starting all handlers...")
        logger.info("[STATUS] Starting all handlers...")
        # Assume che siamo già in home quando si avviano gli handler
        # Dobbiamo notificare PlayerInfo, non solo shared_state
        player_info.set_in_home(True)
        logger.debug("[STATUS] Set in_home_status to True (assumed in home)")
        sleep(0.2)
        try:
            state_handler.toggle_autoroll_handler()
            sleep(0.2)
            state_handler.toggle_building_monitor()
            sleep(0.2)
            state_handler.toggle_bank_heist_handler()
            sleep(0.2)
            state_handler.toggle_shut_down_handler()
            sleep(0.2)
            state_handler.toggle_ui_handler()
            sleep(0.2)
            state_handler.toggle_multiplier_monitor()
            sleep(0.2)
            state_handler.toggle_autoroll_monitor()
            sleep(0.2)
            state_handler.toggle_idle_handler()
            sleep(0.2)
            state_handler.toggle_destruction_handler()
            sleep(0.2)
        except Exception as e:
            print(e)
            logger.error(e)
            exit()
    elif key == keyboard.Key.page_down:
        print("[STATUS] Quick Exit triggered!")
        logger.info("[STATUS] Quick Exit triggered!")
        # Force exit
        import os
        os._exit(0)

    elif key == keyboard.Key.f12:
        print("[STATUS] Exiting...")
        logger.info("[STATUS] Exiting...")
        shared_state.save_cache("image_cache.pkl")
        exit()


def init_cache():
    if os.path.exists("image_cache.pkl"):
        shared_state.load_cache("image_cache.pkl")
    else:
        shared_state.initialize_cache("images")
        shared_state.save_cache("image_cache.pkl")


init_cache()
logger.debug("Cache initialized.")


from utils.visualizer import Visualizer

if __name__ == "__main__":
    logger.info("Starting...")
    visualizer = Visualizer()

    # Start listener in a separate thread so visualizer can run in main thread
    # listener.start() is enough, we don't need join() if visualizer has its own loop
    listener = keyboard.Listener(on_press=on_key_press)
    listener.start()

    state_handler.start_player_info()
    # Wait for PlayerInfo threads to initialize
    logger.info("Waiting for PlayerInfo threads to initialize...")
    sleep(5)
    logger.info("PlayerInfo initialization complete")
    
    state_handler.start_set_console_title()

    # Run visualizer (blocking until closed)
    visualizer.run()
    
    # Cleanup
    shared_state.save_cache("image_cache.pkl")
