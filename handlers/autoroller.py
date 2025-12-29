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
        consecutive_popups = 0
        home_wait_counter = 0
        
        while autoroller_running:  # While autoroller is running
            with shared_state.autoroller_running_condition:
                # Removed wait() to prevent deadlock. We just check the status.
                autoroller_running = shared_state.autoroller_running
            if not autoroller_running:  # If autoroller_running is False,
                break  # break the loop
                
            # Check popup condition
            popup_detected = False
            with shared_state.ui_condition:
                if shared_state.popup_handled:
                    popup_detected = True
                    shared_state.popup_handled = False
            
            if popup_detected:
                consecutive_popups += 1
                logger.debug(f"[AUTOROLL] Popup detected ({consecutive_popups}/3).")
                if consecutive_popups >= 3:
                    logger.info("[AUTOROLL] 3 consecutive popups detected. Assuming NO DICE.")
                    with shared_state.rolls_condition:
                        shared_state.rolls = 0
                        shared_state.rolls_condition.notify_all()
                    break
            else:
                pass 
            
            # User request: Don't gate on in_home_status.
            # Just look for GO button. If found, we are good.
            
            logger.debug("[AUTOROLL] Searching for GO button...")
            point = ocr_utils.find(go_image)
            
            if point is not None:
                logger.debug(f"[AUTOROLL] GO button found at ({point[0]}, {point[1]}). Executing Long Press...")
                
                # Clicca e tieni premuto (Long Press) per attivare Auto-Roll
                with shared_state.moveTo_lock:
                    moveTo(point[0], point[1])
                    sleep(0.3)
                    import pydirectinput
                    pydirectinput.mouseDown()
                    sleep(1.0) # Tieni premuto 1 secondo
                    pydirectinput.mouseUp()
                    # click()
                    sleep(1)
                logger.debug("[AUTOROLL] Long Press executed.")
                
                # Muovi il mouse al centro per non bloccare la vista
                shared_state.moveto_center()
                
                # Attendi che il gioco inizi a rollare
                # Se abbiamo attivato l'auto-roll, potrebbe andare avanti da solo.
                # Ma il bot deve continuare a monitorare.
                sleep(2) 
            else:
                logger.debug("[AUTOROLL] GO button NOT found.")
                # Se GO non trovato, attendi un po' prima di riprovare
                sleep(1)
                
            # Check popup again after action
            with shared_state.ui_condition:
                 if shared_state.popup_handled:
                     consecutive_popups += 1
                     shared_state.popup_handled = False
                     logger.debug(f"[AUTOROLL] Popup detected after click ({consecutive_popups}/3).")
            
            if consecutive_popups >= 3:
                logger.info("[AUTOROLL] 3 consecutive popups detected. Assuming NO DICE.")
                with shared_state.rolls_condition:
                    shared_state.rolls = 0
                    shared_state.rolls_condition.notify_all()
                break
                
            with shared_state.rolling_condition:
                shared_state.rolling_condition.wait_for(
                    lambda: not shared_state.rolling_status, timeout=5
                )
        logger.debug("[AUTOROLL] Exiting autoroll...")

