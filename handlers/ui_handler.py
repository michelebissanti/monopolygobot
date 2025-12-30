from utils.ocr_utils import OCRUtils
from pyautogui import moveTo
from pydirectinput import click
from shared_state import shared_state
import os
from utils.logger import logger
from time import sleep

ocr_utils = OCRUtils()


class UIHandler:
    def __init__(self):
        self.last_clicked_image = None

    def run(self):
        current_path = shared_state.current_path
        ui_images_path = os.path.join(current_path, "images", "ui")

        shared_state.thread_barrier.wait()
        logger.debug("[UI] Received notification! Starting...")

        image_files = [
            os.path.join(ui_images_path, file)
            for file in os.listdir(ui_images_path)
            if os.path.isfile(os.path.join(ui_images_path, file))
        ]

        import random
        
        # Stuck detection
        consecutive_ui_clicks = 0
        max_consecutive_clicks = 5

        while True:
            if shared_state.idle_event.is_set():
                shared_state.idle_event.wait()
            if not shared_state.idle_event.is_set():
                # Shuffle image files to avoid fixating on one element if multiple are present
                random.shuffle(image_files)
                
                found_any = False
                for image_path in image_files:
                    if shared_state.idle_event.is_set():
                        shared_state.idle_event.wait()
                    target_image = shared_state.load_image(image_path)
                    
                    # Use a slightly higher threshold for UI to avoid false positives? 
                    # user asked for MORE tolerance, so default 0.5 is good.
                    location = ocr_utils.find(target_image)
                    if location:
                        print(f"[UI] Detected {image_path}. Clicking...")
                        with shared_state.moveTo_lock:
                            moveTo(location[0], location[1])
                            click()
                        self.last_clicked_image = image_path
                        shared_state.moveto_center()
                        
                        consecutive_ui_clicks += 1
                        found_any = True
                        
                        if consecutive_ui_clicks >= max_consecutive_clicks:
                             logger.warning(f"[UI] Stuck on UI elements ({consecutive_ui_clicks} consecutive clicks). Attempting BLIND CLICK.")
                             with shared_state.moveTo_lock:
                                center_x = shared_state.window_x + shared_state.window_center_x
                                center_y = shared_state.window_y + shared_state.window_center_y
                                moveTo(center_x, center_y)
                                click()
                                sleep(1)
                             consecutive_ui_clicks = 0 # Reset after blind click attempt

                        # Signal that a popup was handled
                        with shared_state.ui_condition:
                            shared_state.popup_handled = True
                            shared_state.ui_condition.notify_all() 
                        break
                
                # --- NEW: Check for "x" Close Button via OCR ---
                # Region: L=45.89, T=93.81, W=8.41, H=4.79
                if not found_any:
                    ocr_text = ocr_utils.ocr_to_str(
                        45.89,
                        93.81,
                        45.89 + 8.41,
                        93.81 + 4.79,
                        ocr_settings=r'--psm 10' # Single character mode might be better, or 6
                    )
                    
                    if "x" in ocr_text.lower():
                        logger.debug(f"[UI] OCR Detected 'x' button: '{ocr_text}'. Clicking...")
                        
                        # Calculate center of region
                        wx, wy, ww, wh = shared_state.window
                        
                        # Percent to pixels
                        cx_p = 45.89 + (8.41 / 2)
                        cy_p = 93.81 + (4.79 / 2)
                        
                        target_x = wx + (ww * (cx_p / 100))
                        target_y = wy + (wh * (cy_p / 100))
                        
                        with shared_state.moveTo_lock:
                            moveTo(target_x, target_y)
                            click()
                        
                        found_any = True
                        consecutive_ui_clicks += 1
                        
                        # Signal handled
                        with shared_state.ui_condition:
                            shared_state.popup_handled = True
                            shared_state.ui_condition.notify_all()
                # -----------------------------------------------
                    consecutive_ui_clicks = 0 # Reset if screen is clear
                    
            sleep(0.5)
            sleep(0.5)
