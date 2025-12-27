from utils.ocr_utils import OCRUtils
from pyautogui import moveTo
from pydirectinput import click
from shared_state import shared_state
import os
from utils.logger import logger
from time import sleep

ocr_utils = OCRUtils()


class AutoRoller:
    @staticmethod
    def run() -> bool:
        current_path = shared_state.current_path
        go_path = os.path.join(current_path, "images", "go.png")
        go_image = shared_state.load_image(go_path)
        autoroller_running = True
        while autoroller_running:  # While autoroller is running
            with shared_state.autoroller_running_condition:
                shared_state.autoroller_running_condition.wait()  # Update autoroller_running status
                autoroller_running = shared_state.autoroller_running
            if not autoroller_running:  # If autoroller_running is False,
                break  # break the loop
            with shared_state.in_home_condition:  # Wait for in_home_status to be updated
                shared_state.in_home_condition.wait_for(
                    lambda: shared_state.in_home_status
                )

            point = ocr_utils.find(go_image)
            if point is not None:
                logger.debug(f"[AUTOROLL] GO button found at ({point[0]}, {point[1]}). Clicking to activate autoroll...")
                
                # Clicca direttamente sul pulsante GO rilevato
                with shared_state.moveTo_lock:
                    moveTo(point[0], point[1])
                    sleep(0.3)
                    click()
                    sleep(1)
                
                # Muovi il mouse al centro per non bloccare la vista
                shared_state.moveto_center()
                
                # Attendi che il gioco inizi a rollare
                sleep(10)
            else:
                # Se GO non trovato, attendi un po' prima di riprovare
                sleep(1)
                
            with shared_state.rolling_condition:
                shared_state.rolling_condition.wait_for(
                    lambda: not shared_state.rolling_status, timeout=5
                )
        logger.debug("[AUTOROLL] Exiting autoroll...")

