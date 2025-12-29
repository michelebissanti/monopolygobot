import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from shared_state import shared_state
from utils.ocr_utils import OCRUtils
from time import sleep

def check_vision():
    print("Initializing Debug Vision Check...")
    ocr = OCRUtils()
    
    # 1. Check Window
    print(f"Target Window Title: {shared_state.WINDOW_TITLE}")
    print(f"Window Coords: {shared_state.window_coords}")
    
    # 2. Check Home Icon
    icon_path = os.path.join(shared_state.current_path, "images", "in-home-icon.png")
    if os.path.exists(icon_path):
        icon = shared_state.load_image(icon_path)
        print(f"Loaded icon from {icon_path}")
        location = ocr.find(icon)
        if location:
            print(f"SUCCESS: Home Icon found at {location}")
        else:
            print("FAILURE: Home Icon NOT found.")
            # Save screenshot for debug
            debug_shot = os.path.join(shared_state.current_path, "debug", "debug_home_fail.png")
            ocr.screenshot(debug_shot)
            print(f"Saved fullscreen screenshot to {debug_shot}")
    else:
        print(f"ERROR: Icon file missing at {icon_path}")

    # 3. Check Rolls OCR
    # ... (existing code) ...
    
    # 2.1 Check GO Button
    print("Checking GO Button...")
    go_path = os.path.join(shared_state.current_path, "images", "go.png")
    if os.path.exists(go_path):
        go_img = shared_state.load_image(go_path)
        go_loc = ocr.find(go_img)
        if go_loc:
             print(f"SUCCESS: GO Button found at {go_loc}")
        else:
             print("FAILURE: GO Button NOT found.")
             ocr.screenshot(os.path.join(shared_state.current_path, "debug", "debug_go_fail.png"))
    else:
        print("ERROR: go.png missing.")
    # Copied coords from player_info.py
    x_percent, y_percent, right_percent, bottom_percent = (43, 92, 57, 94.5)
    
    print("Attempting to read Rolls...")
    debug_crop = "debug_rolls_crop.png" # saved in CWD usually, or pass full path
    
    # We use the same settings as player_info.py
    process_settings = {
        "threshold_value": 75,
        "invert": True,
        "scale_factor": 3,
    }
    
    text = ocr.ocr_to_str(
        x_percent,
        y_percent,
        right_percent,
        bottom_percent,
        output_image_path=os.path.join(shared_state.current_path, "debug", debug_crop),
        ocr_settings=r'--psm 6 -c tessedit_char_whitelist="0123456789/"',
        process_settings=process_settings
    )
    print(f"Rolls OCR Raw Result: '{text}'")
    
    # Check Money while we are at it
    print("Attempting to read Money...")
    xm, ym, rm, bm = (33.5, 5, 62, 9)
    money_text = ocr.ocr_to_str(
        xm, ym, rm, bm,
        output_image_path=os.path.join(shared_state.current_path, "debug", "debug_money_crop.png")
    )
    print(f"Money OCR Raw Result: '{money_text}'")

if __name__ == "__main__":
    check_vision()
