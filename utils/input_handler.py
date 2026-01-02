import os
import time
import msvcrt
import pyautogui
import pydirectinput
from .logger import logger

class GlobalInputAccessor:
    """
    A class to handle global input access across multiple processes using msvcrt file locking.
    This ensures that only one bot controls the mouse/keyboard at a time WITHOUT external dependencies.
    """
    def __init__(self, lock_file="input.lock"):
        self.lock_file_path = os.path.abspath(lock_file)
        # Open the file for writing. Create if doesn't exist. 
        # We keep this file handle open for the lifetime of the object.
        self.f = open(self.lock_file_path, 'w')

    def acquire(self, timeout=10):
        """Acquire the input lock."""
        start_time = time.time()
        while True:
            try:
                # Try to lock the first byte of the file
                # msvcrt.LK_NBLCK (2048): Non-blocking lock. Raises IOError if failed.
                msvcrt.locking(self.f.fileno(), msvcrt.LK_NBLCK, 1)
                return True
            except (IOError, OSError):
                # Lock failed, someone else has it
                if time.time() - start_time > timeout:
                    logger.warning(f"[INPUT] Could not acquire lock within {timeout}s")
                    return False
                time.sleep(0.05)

    def release(self):
        """Release the input lock."""
        try:
            # Unlock the first byte
            # msvcrt.LK_UNLCK (0)
            self.f.seek(0)
            msvcrt.locking(self.f.fileno(), msvcrt.LK_UNLCK, 1)
        except Exception as e:
            logger.error(f"[INPUT] Error releasing lock: {e}")

    def safe_move_to(self, x, y, duration=0.1):
        """Safely move the mouse ensuring exclusive access."""
        if self.acquire():
            try:
                pyautogui.moveTo(x, y, duration=duration)
            finally:
                self.release()

    def safe_click(self, x=None, y=None):
        """Safely click ensuring exclusive access."""
        if self.acquire():
            try:
                if x is not None and y is not None:
                    pyautogui.click(x, y)
                else:
                    pyautogui.click()
            finally:
                self.release()
    
    def safe_pydirectinput_click(self, x=None, y=None):
        """Safely click using pydirectinput (often better for games)."""
        if self.acquire():
             try:
                 if x is not None and y is not None:
                     # pydirectinput might need to move first if coords provided
                     pydirectinput.moveTo(x, y)
                 pydirectinput.click()
             finally:
                 self.release()

# Global instance
input_lock_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "global_input.lock")
global_input = GlobalInputAccessor(input_lock_file)
