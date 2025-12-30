import logging

# This goes first
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s:%(levelname)s:%(name)s - %(message)s",
    filename="log.txt",
    filemode="w",
)
# Set up logging
INFO_LEVEL = 25
DEBUG_LEVEL = 15
logging.addLevelName(INFO_LEVEL, "INFO")
logging.addLevelName(DEBUG_LEVEL, "DEBUG")
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)  # Adjust the log level as needed
formatter = logging.Formatter("%(asctime)s:%(levelname)s:%(name)s - %(message)s")
console_handler.setFormatter(formatter)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(console_handler)


def log_info(message):
    logger.log(INFO_LEVEL, message)


    logger.log(DEBUG_LEVEL, message)

class SharedStateLogHandler(logging.Handler):
    def emit(self, record):
        from shared_state import shared_state
        log_entry = self.format(record)
        shared_state.recent_logs.append(log_entry)
        # Keep only last 5 logs
        if len(shared_state.recent_logs) > 5:
            shared_state.recent_logs.pop(0)

# Add shared state handler
shared_state_handler = SharedStateLogHandler()
shared_state_handler.setFormatter(formatter)
logger.addHandler(shared_state_handler)
