from utils.ocr_utils import OCRUtils
import random
from pyautogui import moveTo
from pydirectinput import click
import time
from time import sleep
from shared_state import shared_state
import os
from utils.logger import logger

ocr_utils = OCRUtils()


import random

class BankHeistHandler:
    def __init__(self):
        self.current_path = shared_state.current_path
        self.bh_door_path = os.path.join(self.current_path, "images", "bank-heist-door.png")
        self.bh_match_path = os.path.join(self.current_path, "images", "heist-match.png")

    def run(self):
        shared_state.thread_barrier.wait()
        logger.debug("[HEIST] Received notification! Starting...")
        while shared_state.bank_heist_handler_running:
            # Optimization: If we are KNOWN to be in 'Home' view (Dice/Money/GO visible),
            # then a Heist cannot be active. Skip unnecessary OCR.
            if shared_state.in_home_status:
                # logger.debug("[HEIST] Player in Home (HUD visible), skipping Heist check.")
                sleep(2)
                continue

            # 1. First check if we are actually in the Heist Minigame
            # STRICT CHECK: Higher threshold to avoid false positives
            if self.is_heist_active(threshold=0.8):
                # 2. Try to find a door to click
                door_point = self.detect_door()
                
                if door_point:
                    self.click_point(door_point, "Door (OCR)")
                else:
                    # 3. Fallback: Blind Click on Grid
                    # ONLY if we are ABSOLUTELY sure we are in Heist mode
                    blind_point = self.get_random_grid_point()
                    self.click_point(blind_point, "Door (Blind)")
                
                # Wait a bit between clicks
                sleep(2)
            else:
                # Not in heist mode, wait before checking again
                sleep(1)

    def is_heist_active(self, threshold=None):
        """Checks for 'MATCH 3' or 'STEAL' text at the top."""
        # Using OCR instead of Image Matching for better reliability
        # Coordinates: (33.09, 23.45, 36.01, 3.09)
        # ocr_to_str args: left, top, right, bottom
        text = ocr_utils.ocr_to_str(
            33.09,
            23.45,
            33.09 + 36.01,
            23.45 + 3.09,
            ocr_settings=r'--psm 6'
        )
        
        logger.debug(f"[HEIST] Active Check OCR: '{text}'")
        
        # Check for keywords
        # "MATCH 3 TO STEAL"
        upper_text = text.upper()
        if "MATCH" in upper_text or "STEAL" in upper_text or "BANK" in upper_text or "MEGA" in upper_text:
            return True
        
        return False

    def detect_door(self):
        """Finds a closed door."""
        image = shared_state.load_image(self.bh_door_path)
        return ocr_utils.find(image)

    def click_point(self, point, source="Unknown"):
        print(f"[HEIST] Clicking {source} at {point}...")
        logger.info(f"[HEIST] Clicking {source} at {point}...")
        
        with shared_state.moveTo_lock:
            moveTo(point[0], point[1], duration=0.2)
            
            shared_state.debug_overlays.append(
                ((point[0], point[1]), f"Click {source}", time.time())
            )
            
            import pydirectinput
            pydirectinput.mouseDown()
            sleep(0.1)
            pydirectinput.mouseUp()
            
        # Move away to see result
        shared_state.moveto_center()

    def get_random_grid_point(self):
        """
        Calculates a random point within a 3x4 grid in the bottom section of the window.
        """
        wx, wy, ww, wh = shared_state.window
        
        # Grid definition (approximate based on UI)
        # Start Y: ~55% down (below headers/match area)
        # End Y: ~95% down
        # Start X: ~10% across
        # End X: ~90% across
        
        start_x = wx + (ww * 0.1)
        end_x = wx + (ww * 0.9)
        start_y = wy + (wh * 0.55)
        end_y = wy + (wh * 0.95)
        
        width = end_x - start_x
        height = end_y - start_y
        
        # 4 columns, 3 rows
        col = random.randint(0, 3)
        row = random.randint(0, 2)
        
        # Center of the cell
        cell_w = width / 4
        cell_h = height / 3
        
        center_x = int(start_x + (col * cell_w) + (cell_w / 2))
        center_y = int(start_y + (row * cell_h) + (cell_h / 2))
        
        return (center_x, center_y)
