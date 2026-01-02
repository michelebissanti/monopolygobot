import logging
import os

# Define levels
INFO_LEVEL = 25
DEBUG_LEVEL = 15
logging.addLevelName(INFO_LEVEL, "INFO")
logging.addLevelName(DEBUG_LEVEL, "DEBUG")

# Create logger
logger = logging.getLogger("MonopolyGoBot")
logger.setLevel(logging.DEBUG)

# Console Handler (Standard)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO) 
formatter = logging.Formatter("%(asctime)s:%(levelname)s:%(name)s - %(message)s")
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

def configure_logger(window_title):
    """
    Configures the file handler for the logger based on the window title.
    This allows each bot instance to log to a separate file.
    """
    # Sanitize title for filename
    safe_title = "".join(c for c in window_title if c.isalnum() or c in (' ', '_', '-')).strip()
    log_filename = f"log_{safe_title}.txt"
    
    file_handler = logging.FileHandler(log_filename, mode='w')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    
    # Remove old file handlers if any (to avoid duplicate logging if re-configured)
    for h in logger.handlers[:]:
        if isinstance(h, logging.FileHandler):
            logger.removeHandler(h)
            
    logger.addHandler(file_handler)
    logger.info(f"Logging initialized to {log_filename}")

def log_info(message):
    logger.log(INFO_LEVEL, message)

class SharedStateLogHandler(logging.Handler):
    def emit(self, record):
        # Local import to avoid circular dependency
        try:
             from shared_state import shared_state
             log_entry = self.format(record)
             if hasattr(shared_state, 'recent_logs'):
                 shared_state.recent_logs.append(log_entry)
                 if len(shared_state.recent_logs) > 5:
                     shared_state.recent_logs.pop(0)
        except ImportError:
            pass

# Add shared state handler
shared_state_handler = SharedStateLogHandler()
shared_state_handler.setFormatter(formatter)
logger.addHandler(shared_state_handler)
