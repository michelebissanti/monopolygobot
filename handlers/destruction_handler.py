"""
destruction_handler.py

Handles the destruction mode by detecting and clicking on targets.
"""

import pyautogui
from time import sleep
from utils.logger import logger
from shared_state import shared_state
from utils.ocr_utils import OCRUtils
import os

ocr_utils = OCRUtils()


class DestructionHandler:
    def __init__(self):
        self.last_clicked_target = None
        self.target_image_path = None
        
    def find_and_click_target(self):
        """
        Trova e clicca su un mirino sullo schermo.
        Returns:
            bool: True se ha trovato e cliccato un mirino, False altrimenti
        """
        try:
            current_path = shared_state.current_path
            # Cerca il file target.png nella cartella images
            target_image_path = os.path.join(current_path, "images", "target.png")
            
            # Verifica se il file esiste
            if not os.path.exists(target_image_path):
                logger.warning(f"[DESTRUCTION] Target image not found at: {target_image_path}")
                return False
            
            # Carica l'immagine
            target_image = shared_state.load_image(target_image_path)
            
            if shared_state.idle_event.is_set():
                return False
            
            # Cerca il mirino sullo schermo
            location = ocr_utils.find(target_image, threshold=0.5)
            
            if location:
                print(f"[DESTRUCTION] Target found. Clicking...")
                logger.info(f"[DESTRUCTION] Target found at ({location[0]}, {location[1]}). Clicking...")
                
                with shared_state.moveTo_lock:
                    pyautogui.moveTo(location[0], location[1])
                    pyautogui.click()
                
                self.last_clicked_target = target_image_path
                shared_state.moveto_center()
                return True
            else:
                return False
                
        except Exception as e:
            logger.error(f"[DESTRUCTION] Error finding target: {e}")
            return False
    
    def run(self):
        """
        Main loop for destruction handler - monitora continuamente e clicca sui mirini.
        """
        logger.debug("[DESTRUCTION] Starting destruction handler...")
        
        shared_state.thread_barrier.wait()
        
        logger.debug("[DESTRUCTION] Destruction handler is now active!")
        
        while True:
            if shared_state.idle_event.is_set():
                shared_state.idle_event.wait()
                
            if not shared_state.idle_event.is_set():
                if self.find_and_click_target():
                    sleep(1)
            
            sleep(2)