from dotenv import load_dotenv
from os import getenv as env
from threading import Condition, Lock, Barrier, Event, RLock
import pygetwindow as gw
from utils.image_cache import ImageCache
import os
from pyautogui import moveTo
import argparse
import sys
from utils.logger import logger

load_dotenv()
image_cache = ImageCache()

# Import the Global Input Accessor
from utils.input_handler import global_input

class SharedState:
    AR_MINIMUM_ROLLS = int(env("AR_MINIMUM_ROLLS", 0))
    AR_RESUME_ROLLS = int(env("AR_RESUME_ROLLS", 0))
    # BUILD_START_AMOUNT = int(env("BUILD_START_AMOUNT"))
    BUILD_FINISH_AMOUNT = int(env("BUILD_FINISH_AMOUNT", 0))
    # Default fallback
    DEFAULT_WINDOW_TITLE = env("WINDOW_TITLE", "BlueStacks App Player")

    def __init__(self):
        # Parse arguments to get specific window title if provided
        # We use a simplified parser here because shared_state is imported early
        window_title = self.DEFAULT_WINDOW_TITLE
        
        # Check sys.args manually to avoid conflict with main parser if necessary
        # specific arg: --window "Title"
        if "--window" in sys.argv:
            try:
                idx = sys.argv.index("--window")
                if idx + 1 < len(sys.argv):
                    window_title = sys.argv[idx + 1]
            except Exception:
                pass
        
        self.WINDOW_TITLE = window_title
        logger.info(f"[SHARED] Target Window Title: '{self.WINDOW_TITLE}'")

        try:
            windows = gw.getWindowsWithTitle(self.WINDOW_TITLE)
            if not windows:
                raise Exception(f"Window with title '{self.WINDOW_TITLE}' not found!")
            
            # Filter for EXACT match first
            exact_match = None
            for w in windows:
                if w.title == self.WINDOW_TITLE:
                    exact_match = w
                    break
            
            if exact_match:
                self.window_obj = exact_match
                logger.debug(f"[SHARED] Found EXACT match for '{self.WINDOW_TITLE}'")
            else:
                # Fallback to first match (substring)
                self.window_obj = windows[0]
                logger.warning(f"[SHARED] No exact match for '{self.WINDOW_TITLE}', using '{self.window_obj.title}'")
            
            self.window_x = self.window_obj.left
            self.window_y = self.window_obj.top
            self.window_width = self.window_obj.width
            self.window_height = self.window_obj.height
            self.window_center_x = int(self.window_width / 2)
            self.window_center_y = int(self.window_height / 2)
            self.window_right = self.window_x + self.window_width
            self.window_bottom = self.window_y + self.window_height
            self.window = (
                self.window_x,
                self.window_y,
                self.window_width,
                self.window_height,
            )
            self.window_coords = (
                self.window_x,
                self.window_y,
                self.window_right,
                self.window_bottom,
            )
        except Exception as e:
            logger.critical(f"[SHARED] Failed to initialize window: {e}")
            # Initialize with dummy values to prevent immediate crash on import
            self.window = (0, 0, 1920, 1080)
            self.window_coords = (0, 0, 1920, 1080)
            self.window_x = 0; self.window_y = 0; self.window_width = 1920; self.window_height=1080

        self.current_path = os.path.dirname(os.path.abspath(__file__))
        # Variables
        self.autoroll_handler_running = False
        self.autoroller_running = False
        self.autoroller_thread_is_alive = False
        self.disable_autoroller_running = False
        self.disable_autoroller_thread_is_alive = False
        self.autoroll_monitor_running = False

        self.builder_running = False
        self.building_monitor_running = False
        self.building_handler_thread_is_alive = False
        self.builder_finished = False

        self.bank_heist_handler_running = False
        self.shut_down_handler_running = False
        self.ui_handler_running = False
        self.idle_handler_running = False
        self.destruction_handler_running = False
        self.popup_handled = False

        self.multiplier_handler_running = False
        self.multiplier_monitor_running = False

        self.money = None  # Inizializzato a None, verrà impostato da PlayerInfo
        self.rolls = None  # Inizializzato a None, verrà impostato da PlayerInfo
        self.multiplier = 1
        self.BUILD_START_AMOUNT = 1
        self.rolling_status = False
        self.in_home_status = True
        # Conditions
        self.autoroll_handler_condition = Condition()
        self.autoroll_handler_running_condition = Condition()
        self.autoroller_running_condition = Condition()
        self.disable_autoroller_running_condition = Condition()
        self.autoroll_monitor_condition = Condition()

        self.building_monitor_condition = Condition()
        self.builder_running_condition = Condition()
        self.builder_finished_condition = Condition()

        self.bank_heist_condition = Condition()
        self.shut_down_condition = Condition()
        self.ui_condition = Condition()
        self.idle_condition = Condition()
        self.destruction_condition = Condition()

        self.multiplier_condition = Condition()
        self.multiplier_monitor_condition = Condition()
        self.multiplier_handler_running_condition = Condition()
        self.multiplier_handler_finished_condition = Condition()

        self.rolls_condition = Condition()
        self.money_condition = Condition()
        self.rolling_condition = Condition()
        self.in_home_condition = Condition()
        # Locks
        self.multiplier_monitor_lock = Lock()
        self.autoroller_lock = Lock()
        self.moveTo_lock = Lock()
        self.press_lock = Lock()
        self.start_autoroller_lock = RLock()
        self.stop_autoroller_lock = RLock()
        self.start_disable_autoroller_lock = RLock()
        self.stop_disable_autoroller_lock = RLock()
        # Thread barrier
        self.thread_barrier = Barrier(9)
        # Events
        self.multiplier_handler_event = Event()
        self.builder_event = Event()
        self.idle_event = Event()
        
        # Debug / Visualizer
        self.debug_overlays = [] # List of tuples: (rect/point, label, timestamp)
        self.recent_logs = [] # List of strings
        self.bot_status = "RUNNING" # Current status string (e.g. "RUNNING", "PAUSED", "IDLE")

    def load_image(self, path: str):
        return image_cache.load_image(path)

    def save_cache(self, path: str):
        image_cache.save_cache(path)

    def load_cache(self, path: str):
        image_cache.load_cache(path)

    def initialize_cache(self, directory: str, recursive=True):
        image_cache.initialize_cache(directory, recursive)

    def moveto_center(self):
        # Use Global Input Lock for Safe MoveTo
        # Calculate center manually or use global_input if simple move
        center_x = self.window_x + self.window_center_x
        center_y = self.window_y + self.window_center_y
        
        # Use global input handler
        global_input.safe_move_to(center_x, center_y, duration=0.2)


shared_state = SharedState()
