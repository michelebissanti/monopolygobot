from utils.ocr_utils import OCRUtils
from pyautogui import moveTo
from pydirectinput import click
from time import sleep
from shared_state import shared_state
import os
from utils.logger import logger

ocr_utils = OCRUtils()


class BankHeistHandler:
    def __init__(self):
        self.current_path = shared_state.current_path
        self.bh_path = os.path.join(self.current_path, "images", "bank-heist-door.png")

    def run(self):
        shared_state.thread_barrier.wait()
        logger.debug("[HEIST] Received notification! Starting...")
        while shared_state.bank_heist_handler_running:
            point = self.detect_bank_heist()
            if point is not None:
                print(f"[HEIST] Bank heist detected at ({point[0]}, {point[1]}). Clicking...")
                logger.info(f"[HEIST] Bank heist detected at ({point[0]}, {point[1]}). Clicking...")
                
                # Clicca direttamente sulla porta del bank heist
                with shared_state.moveTo_lock:
                    moveTo(point[0], point[1])
                    sleep(0.2)  # Ridotto da 0.5 a 0.2
                    click()
                    sleep(0.5)  # Ridotto da 2 a 0.5
                
                # Muovi il mouse al centro per non bloccare la vista
                shared_state.moveto_center()
                
                # Attendi prima di cercare di nuovo (evita click multipli)
                sleep(2)  # Ridotto da 5 a 2
            else:
                # Se non trovato, attendi un po' prima di cercare di nuovo
                sleep(0.5)  # Ridotto da 1 a 0.5

    def detect_bank_heist(self):
        """
        Rileva la porta del Bank Heist sullo schermo.
        Returns:
            tuple: Coordinate (x, y) della porta se trovata, None altrimenti
        """
        image = shared_state.load_image(self.bh_path)
        point = ocr_utils.find(image)
        return point
