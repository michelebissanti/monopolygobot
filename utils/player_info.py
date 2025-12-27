from .ocr_utils import OCRUtils
from shared_state import shared_state
from time import sleep
import re
import os
from .logger import logger
from threading import Thread

ocr_utils = OCRUtils()


class PlayerInfo:
    def __init__(self):
        """
        PlayerInfo class is responsible for getting the player's money, rolls, multiplier, rolling status, and in home status.

        Attributes:
            money (int): The player's money.
            rolls (int): The player's rolls.
            multiplier (int): The player's multiplier.
            rolling_status (bool): The player's rolling status.
            in_home_status (bool): The player's in home status.
            money_condition (threading.Condition): The condition variable for the money attribute.
            rolls_condition (threading.Condition): The condition variable for the rolls attribute.
            multiplier_condition (threading.Condition): The condition variable for the multiplier attribute.
            rolling_status_condition (threading.Condition): The condition variable for the rolling_status attribute.
            in_home_condition (threading.Condition): The condition variable for the in_home_status attribute.
        """
        self.current_path = shared_state.current_path

        self.money = None
        self.rolls = None
        self.multiplier = None
        self.rolling_status = False
        self.in_home_status = False
        self.money_condition = shared_state.money_condition
        self.rolls_condition = shared_state.rolls_condition
        self.multiplier_condition = shared_state.multiplier_condition
        self.rolling_status_condition = shared_state.rolling_condition
        self.in_home_condition = shared_state.in_home_condition

    def money_thread(self):
        """
        Thread function to continuously monitor and update the player's money.
        """
        last_known_money = 0  # Inizializza a 0
        while True:
            if self.in_home_status:
                x_percent = 33.5
                y_percent = 5
                right_percent = 62
                bottom_percent = 9
                money_text = ocr_utils.ocr_to_str(
                    x_percent,
                    y_percent,
                    right_percent,
                    bottom_percent,
                    output_image_path="proc-money.png",
                )
                money_text = "".join(filter(str.isdigit, money_text))

                if money_text.isdigit():
                    new_money = int(money_text)
                    self.set_money(new_money)
                    last_known_money = self.money
                    # Log ogni 60 secondi circa
                    if not hasattr(self, '_money_log_counter'):
                        self._money_log_counter = 0
                    self._money_log_counter += 1
                    if self._money_log_counter % 60 == 0:
                        logger.debug(f"[PLAYER-INFO] Money updated: {new_money:,}")
                else:
                    self.set_money(last_known_money)
                sleep(0.5)  # Controlla ogni 0.5 secondi
            else:
                logger.debug("[PLAYER-INFO] Money thread waiting for in_home_status...")
                with self.in_home_condition:
                    self.in_home_condition.wait_for(lambda: self.in_home_status)
                logger.debug("[PLAYER-INFO] Money thread: in_home_status became True!")
                sleep(1)

    def rolls_thread(self):
        """
        Thread function to continuously monitor and update the player's rolls.
        """
        last_known_rolls = 0  # Inizializza a 0
        last_known_roll_capacity = 50  # Inizializza a 50
        while True:
            if self.in_home_status:
                x_percent, y_percent, right_percent, bottom_percent = (
                    43,
                    92,
                    57,
                    94.5,
                )
                process_settings = {
                    "threshold_value": 100,
                    "invert": True,
                    "scale_factor": 3,
                }
                rolls_text = ocr_utils.ocr_to_str(
                    x_percent,
                    y_percent,
                    right_percent,
                    bottom_percent,
                    output_image_path="rolls-proc.png",
                    process_settings=process_settings,
                    ocr_settings=r'--psm 6 -c tessedit_char_whitelist="0123456789/"',
                )

                rolls_text_e = re.sub(r"([^0-9/])", "", rolls_text)
                rolls_parts = rolls_text_e.split("/")

                if len(rolls_parts) == 2:
                    try:
                        rolls = int(rolls_parts[0].strip())
                        roll_capacity = int(rolls_parts[1].strip())
                        self.set_rolls(rolls)
                        last_known_rolls = rolls
                        last_known_roll_capacity = roll_capacity
                        # Log ogni volta che i rolls cambiano
                        if not hasattr(self, '_last_logged_rolls'):
                            self._last_logged_rolls = -1
                        if rolls != self._last_logged_rolls:
                            logger.debug(f"[PLAYER-INFO] Rolls updated: {rolls}/{roll_capacity}")
                            self._last_logged_rolls = rolls

                    except ValueError:
                        self.set_rolls(last_known_rolls)
                else:
                    self.set_rolls(last_known_rolls)
                sleep(0.5)  # Controlla ogni 0.5 secondi
            else:
                with self.in_home_condition:
                    self.in_home_condition.wait_for(lambda: self.in_home_status)
                sleep(1)

    def multiplier_thread(self):
        """
        Thread function to continuously monitor and update the player's multiplier.
        """
        last_known_multiplier = 1  # Inizializza a 1
        while True:
            if self.in_home_status:
                x_percent, y_percent, right_percent, bottom_percent = (
                    53,
                    70,
                    57,
                    73,
                )
                mp_ocr_settings = (
                    r"--psm 7 --oem 3 -c tessedit_char_whitelist=x0123456789"
                )
                mp_process_settings = {
                    "threshold_value": None,
                    "invert": False,
                    "scale_factor": 3,
                }
                multiplier_text = ocr_utils.ocr_to_str(
                    x_percent,
                    y_percent,
                    right_percent,
                    bottom_percent,
                    output_image_path="multi.png",
                    ocr_settings=mp_ocr_settings,
                    process_settings=mp_process_settings,
                )
                multiplier_text = "".join(filter(str.isdigit, multiplier_text))

                if multiplier_text.isdigit():
                    self.set_multiplier(int(multiplier_text))
                    last_known_multiplier = self.multiplier
                    sleep(0.5)
                else:
                    self.set_multiplier(last_known_multiplier)
                    sleep(0.5)
            else:
                with self.in_home_condition:
                    self.in_home_condition.wait_for(lambda: self.in_home_status)
                sleep(1)

    def rolling_status_thread(self):
        """
        Thread function to continuously monitor and update the player's rolling status.
        """
        # Carica l'immagine UNA VOLTA all'inizio
        autoroll_image_path = os.path.join(
            self.current_path, "images", "autoroll.png"
        )
        autoroll_image = shared_state.load_image(autoroll_image_path)
        
        while True:
            if self.in_home_status:
                autoroll_location = ocr_utils.find(autoroll_image)
                if autoroll_location:
                    self.set_rolling(True)
                else:
                    self.set_rolling(False)
                sleep(0.5)  # Controlla ogni 0.5 secondi
            else:
                with self.in_home_condition:
                    self.in_home_condition.wait_for(lambda: self.in_home_status)

    def in_home_status_thread(self):
        """
        Thread function to continuously monitor and update the player's in home status.
        """
        check_count = 0
        logger.debug(f"[PLAYER-INFO] In-Home thread started. Window coords: {shared_state.window_coords}")
        
        # Carica l'immagine UNA VOLTA all'inizio invece che ad ogni iterazione
        in_home_image_path = os.path.join(
            self.current_path, "images", "in-home-icon.png"
        )
        in_home_image = shared_state.load_image(in_home_image_path)
        logger.debug(f"[PLAYER-INFO] In-Home icon loaded: {in_home_image.shape if in_home_image is not None else 'None'}")
        
        # WORKAROUND: Il template matching non funziona con molti thread contemporanei
        # Aspettiamo che in_home_status venga impostato a True da main.py (quando si preme Page Up)
        # poi manteniamo True senza ulteriori controlli
        logger.debug("[PLAYER-INFO] Waiting for in_home_status to be set to True...")
        with self.in_home_condition:
            self.in_home_condition.wait_for(lambda: self.in_home_status)
        
        logger.debug("[PLAYER-INFO] in_home_status is now True. Maintaining True state.")
        
        # Una volta True, manteniamo True senza fare altri controlli
        while True:
            sleep(5)  # Sleep lungo, non facciamo più controlli

    def set_money(self, money):
        """
        Sets the player's money.
        """
        with self.money_condition:
            self.money = money
            shared_state.money = money
            self.money_condition.notify_all()

    def set_rolls(self, rolls):
        """
        Sets the player's rolls.
        """
        with self.rolls_condition:
            self.rolls = rolls
            shared_state.rolls = rolls
            self.rolls_condition.notify_all()

    def set_multiplier(self, multiplier):
        """
        Sets the player's multiplier.
        """
        with self.multiplier_condition:
            self.multiplier = multiplier
            shared_state.multiplier = multiplier
            self.multiplier_condition.notify_all()

    def set_rolling(self, rolling_status):
        """
        Sets the player's rolling status.
        """
        with self.rolling_status_condition:
            self.rolling_status = rolling_status
            shared_state.rolling_status = rolling_status
            self.rolling_status_condition.notify_all()

    def set_in_home(self, in_home_status):
        """
        Sets the player's in home status.
        """
        with self.in_home_condition:
            self.in_home_status = in_home_status
            shared_state.in_home_status = in_home_status
            self.in_home_condition.notify_all()

    def run(self):
        """
        Runs each thread to monitor and update the player's money, rolls, multiplier, rolling status, and in home status.
        """
        logger.debug("[PLAYER-INFO] ========================================")
        logger.debug("[PLAYER-INFO] PlayerInfo STARTING all threads...")
        logger.debug("[PLAYER-INFO] ========================================")
        
        threads = {
            "money": Thread(
                target=self.money_thread, daemon=True, name="playerinfo.money"
            ),
            "rolls": Thread(
                target=self.rolls_thread, daemon=True, name="playerinfo.rolls"
            ),
            "multiplier": Thread(
                target=self.multiplier_thread,
                daemon=True,
                name="playerinfo.multiplier",
            ),
            "rolling_status": Thread(
                target=self.rolling_status_thread,
                daemon=True,
                name="playerinfo.rolling_status",
            ),
            "in_home_status": Thread(
                target=self.in_home_status_thread,
                daemon=True,
                name="playerinfo.in_home_status",
            ),
        }
        for thread_name, thread in threads.items():
            thread.start()
            logger.debug(f"[PLAYER-INFO] Started thread: {thread_name}")
        
        logger.debug("[PLAYER-INFO] All threads started successfully")
