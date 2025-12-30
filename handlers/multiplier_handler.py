from shared_state import shared_state
from pyautogui import moveTo
from pydirectinput import click
from utils.logger import logger
import time
from time import sleep


class MultiplierHandler:
    """
    MultiplierHandler handles changing the multiplier.
    It is started by MultiplierMonitor when the multiplier is incorrect.
    """

    def __init__(self, correct_multiplier, timeout=30):
        self.correct_multiplier = correct_multiplier
        self.multiplier = shared_state.multiplier
        (
            self.window_x,
            self.window_y,
            self.window_width,
            self.window_height,
        ) = shared_state.window
        self.timeout = timeout
        mp_region_percent = (61, 70.5, 71, 73.3)
        left_percent, top_percent, right_percent, bottom_percent = mp_region_percent
        self.center_x = (
            self.window_x + self.window_width * (left_percent + right_percent) / 200
        )
        self.center_y = (
            self.window_y + self.window_height * (top_percent + bottom_percent) / 200
        )

    def run(self):
        with shared_state.in_home_condition:
            logger.debug("[MP-H] Not on home screen. Waiting...")
            shared_state.in_home_condition.wait_for(lambda: shared_state.in_home_status)
        logger.debug("[MP-H] On home screen. Starting...")
        
        # Load max.png
        import os
        from utils.ocr_utils import OCRUtils
        current_path = shared_state.current_path
        max_image_path = os.path.join(current_path, "images", "max.png")
        max_image = shared_state.load_image(max_image_path)
        ocr_utils = OCRUtils()
        
        start_time = time.time()
        
        # Loop until MAX image is found
        # Loop until MAX image is found
        while True:
            # Check if MAX is visible using OCR
            # Coordinates from user: (61.06, 57.29, 12.98, 3.99)
            # ocr_to_str expects: left, top, right, bottom
            text = ocr_utils.ocr_to_str(
                61.06,
                57.29,
                61.06 + 12.98,
                57.29 + 3.99,
                ocr_settings=r'--psm 6' # Simple single line mode
            )
            
            logger.debug(f"[MP-H] OCR Text: '{text}'")
            
            if "MAX" in text.upper():
                 logger.debug("[MP-H] MAX multiplier found! Exiting...")
                 break

            shared_state.multiplier_handler_event.set()
            with shared_state.moveTo_lock:
                moveTo(self.center_x, self.center_y)
                import pydirectinput
                pydirectinput.click() # Using pydirectinput for consistency
                
            # Wait a bit for UI to update
            sleep(0.5)

            elapsed_time = time.time() - start_time
            if elapsed_time >= self.timeout:
                logger.debug("[MP-H] Timeout reached (MAX not found). Exiting...")
                break
            logger.debug("[MP-H] Multiplier clicked. Checking for MAX...")
            
        shared_state.moveto_center()
        shared_state.multiplier_handler_event.clear()
        with shared_state.multiplier_handler_finished_condition:
            logger.debug("[MP-H] Exiting...")
            shared_state.multiplier_handler_running = False
            shared_state.multiplier_handler_finished_condition.notify_all()
