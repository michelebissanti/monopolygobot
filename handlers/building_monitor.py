"""
building_monitor.py

This module contains the BuildingMonitor class, which is responsible for starting the building handler when there are no more dice rolls available.
Runs as a loop in a separate thread.
"""

from threading import Thread
from handlers import building_handler
from shared_state import shared_state
from time import sleep
from utils.logger import logger
from utils.ocr_utils import OCRUtils
import re


class BuildingMonitor:
    def __init__(self):
        self.builder_running_condition = shared_state.builder_running_condition
        self.builder_running = shared_state.builder_running
        self.minimum_money_to_build = 1000  # Denaro minimo necessario per avviare il build
        self.ocr_utils = OCRUtils()

    def set_builder_running(self, value):
        """
        Set the builder_running state and notify other threads.
        Args:
            value (bool): The value to set the builder_running state to.
        """
        with self.builder_running_condition:
            self.builder_running = value
            shared_state.builder_running = value
            sleep(0.2)
            self.builder_running_condition.notify_all()
        if value is True:
            shared_state.builder_event.set()
            shared_state.start_autoroller_lock.acquire(blocking=True)
            shared_state.start_disable_autoroller_lock.acquire(blocking=True)
            shared_state.stop_autoroller_lock.acquire(blocking=True)
            shared_state.stop_disable_autoroller_lock.acquire(blocking=True)
        if value is False:
            shared_state.builder_event.clear()
            shared_state.start_autoroller_lock.release()
            shared_state.start_disable_autoroller_lock.release()
            shared_state.stop_autoroller_lock.release()
            shared_state.stop_disable_autoroller_lock.release()

    def should_start_building(self, rolls, money):
        """
        Determine if building should start based on available rolls and money.
        Building starts when no more dice rolls are available and there's enough money.
        Args:
            rolls (int): Number of available dice rolls
            money (int): Current money amount
        Returns:
            bool: True if building should start, False otherwise
        """
        # Inizia il build quando non ci sono più tiri disponibili E c'è abbastanza denaro
        return rolls < 1 and money >= self.minimum_money_to_build

    def check_wait_time(self):
        """
        Checks the screen for the time remaining until more rolls are available.
        Returns:
            str | None: The time string (e.g. "57:52") or None if not found.
        """
        # Region provided by user: Left(%): 36.56, Top(%): 94.82, Width(%): 27.24, Height(%): 2.19
        x = 36.56
        y = 94.82
        w = 27.24
        h = 2.19
        right = x + w
        bottom = y + h
        
        try:
             # Expanded whitelist to include dot and colon, and potentially space
             # psm 7 corresponds to "Treat the image as a single text line."
             text = self.ocr_utils.ocr_to_str(
                 x, y, right, bottom, 
                 ocr_settings="--psm 7 --oem 3 -c tessedit_char_whitelist=0123456789:. "
             )
             logger.debug(f"[BUILD-M] Raw Wait Time OCR: '{text}'")
             
             # Regex for time format XX:XX or XX.XX (e.g. 52:10, 01:05, 57.52)
             match = re.search(r"(\d{1,2}[:.]\d{2})", text)
             if match:
                 time_val = match.group(1).replace(".", ":") # Standardize to colon
                 return time_val
        except Exception as e:
            logger.error(f"[BUILD-M] Failed to check wait time: {e}")
            
        return None

    def run(self, ar_handler_instance):
        """
        Start the building handler when there are no more dice rolls available.
        Handles starting and stopping the autoroller & disable_autoroller.
        Args:
            ar_handler_instance (AutorollerHandler): The AutorollerHandler instance.
        """
        self.ar_handler_instance = ar_handler_instance
        shared_state.thread_barrier.wait()
        logger.debug("[BUILD-M] ========================================")
        logger.debug("[BUILD-M] Building Monitor STARTED")
        logger.debug("[BUILD-M] ========================================")
        logger.debug(f"[BUILD-M] Minimum money required to build: {self.minimum_money_to_build}")
        logger.debug(f"[BUILD-M] Initial state: rolls={shared_state.rolls}, money={shared_state.money}, in_home={shared_state.in_home_status}")
        
        check_count = 0
        while True:
            check_count += 1
            # Leggi i valori correnti usando le condition variables con timeout
            # IMPORTANTE: leggi DOPO il wait per ottenere il valore aggiornato
            with shared_state.rolls_condition:
                if shared_state.rolls is None:
                    shared_state.rolls_condition.wait(timeout=2)  # Aspetta max 2s per primo aggiornamento
                else:
                    shared_state.rolls_condition.wait(timeout=0.5)  # Aspetta max 0.5s per aggiornamenti successivi
                rolls = shared_state.rolls
            
            with shared_state.money_condition:
                if shared_state.money is None:
                    shared_state.money_condition.wait(timeout=2)  # Aspetta max 2s per primo aggiornamento
                else:
                    shared_state.money_condition.wait(timeout=0.5)  # Aspetta max 0.5s per aggiornamenti successivi
                money = shared_state.money
            
            # Se i valori sono None, aspetta che vengano inizializzati
            if rolls is None or money is None:
                if check_count % 10 == 1:  # Log ogni 10 controlli
                    logger.debug(f"[BUILD-M] Check #{check_count}: Waiting for initialization (rolls={rolls}, money={money})...")
                sleep(1)
                continue
            
            # Log ogni 30 controlli (ogni minuto circa) per non riempire i log
            if check_count % 30 == 0:
                logger.debug(f"[BUILD-M] Check #{check_count}: rolls={rolls}, money={money}, builder_running={shared_state.builder_running}")
                
            # Log sempre quando le condizioni sono soddisfatte
            if self.should_start_building(rolls, money) and not shared_state.builder_running:
                logger.debug(f"[BUILD-M] Check #{check_count}: CONDIZIONI SODDISFATTE! rolls={rolls}, money={money}")
                
            if shared_state.multiplier_handler_event.is_set():
                logger.debug("[BUILD-M] Waiting for multiplier handler to finish...")
                shared_state.multiplier_handler_event.wait()
                sleep(10)
            if not shared_state.multiplier_handler_event.is_set():
                if (  # Start building handler when no rolls available and enough money
                    not shared_state.builder_running
                    and self.should_start_building(rolls, money)
                ):
                    logger.debug(
                        f"[BUILD-M] No more rolls available (rolls={rolls}) and enough money ({money}). Starting builder..."
                    )
                    shared_state.bot_status = "BUILDING"
                    self.set_builder_running(True)
                    if shared_state.autoroller_running:
                        logger.debug("[BUILD-M] Stopping autoroller...")
                        with shared_state.stop_autoroller_lock:
                            ar_handler_instance.stop_autoroller()
                            while (
                                shared_state.autoroller_running
                            ):  # Wait for autoroller to stop
                                with shared_state.autoroller_running_condition:
                                    shared_state.autoroller_running_condition.wait_for(
                                        lambda: not shared_state.autoroller_running
                                    )
                            logger.debug(
                                "[BUILD-M] Autoroller stopped in BuildingMonitor"
                            )
                        if not shared_state.disable_autoroller_running:
                            with shared_state.start_disable_autoroller_lock:
                                ar_handler_instance.start_disable_autoroller()
                                while (
                                    not shared_state.disable_autoroller_running
                                ):  # Wait for disable_autoroller to start
                                    with shared_state.disable_autoroller_running_condition:
                                        shared_state.disable_autoroller_running_condition.wait_for(
                                            lambda: shared_state.disable_autoroller_running
                                        )
                    while (
                        not shared_state.in_home_status
                    ):  # Wait for in_home_status to be updated
                        with shared_state.in_home_condition:
                            shared_state.in_home_condition.wait()
                    building_handler_instance = (
                        building_handler.BuildingHandler()
                    )  # Start building handler
                    if not hasattr(self, "building_handler_thread"):
                        self.building_handler_thread = Thread(
                            target=building_handler_instance.run,
                            daemon=False,
                            name="building_handler",
                        )
                        self.building_handler_thread.start()

                        logger.debug(
                            "[BUILD-M] Builder handler thread started in BuildingMonitor"
                        )
                    elif not self.building_handler_thread.is_alive():
                        self.building_handler_thread = Thread(
                            target=building_handler_instance.run,
                            daemon=False,
                            name="building_handler",
                        )
                        self.building_handler_thread.start()

                    with shared_state.builder_running_condition:
                        shared_state.builder_running = self.builder_running
                        shared_state.builder_running_condition.notify_all()

                    with shared_state.builder_finished_condition:  # Wait for building handler to finish
                        shared_state.builder_finished_condition.wait_for(
                            lambda: shared_state.builder_finished
                        )
                        logger.debug("[BUILD-M] Builder handler finished")

                    if (
                        shared_state.disable_autoroller_running
                    ):  # Start autoroller if disable_autoroller is running
                        logger.debug("[BUILD-M] Stopping disable_autoroller...")
                        with shared_state.stop_disable_autoroller_lock:
                            ar_handler_instance.stop_disable_autoroller()
                            with shared_state.disable_autoroller_running_condition:
                                shared_state.disable_autoroller_running_condition.wait_for(
                                    lambda: not shared_state.disable_autoroller_running
                                )
                    self.set_builder_running(False)  # Set builder_running to False
                    logger.debug("[BUILD-M] Build cycle completed. Entering Wait Mode until rolls increase...")
                    
                    # Force a wait loop until rolls are replenished
                    while True:
                        with shared_state.rolls_condition:
                            if shared_state.rolls is None:
                                shared_state.rolls_condition.wait(timeout=2)
                            else:
                                shared_state.rolls_condition.wait(timeout=0.5)
                            current_rolls = shared_state.rolls
                            
                        # If we have enough rolls (e.g. >= 5 for safety, or even >=1), we assume we can play again
                        # AutorollMonitor will pick up when rolls >= 1 usually. 
                        # We break here to let the main loop decide.
                        if current_rolls is not None and current_rolls >= 5: 
                             logger.debug(f"[BUILD-M] Rolls replenished ({current_rolls}). Exiting Wait Mode.")
                             break
                             
                        # Update status
                        wait_time_s = 2
                        time_str = self.check_wait_time()
                        if time_str:
                             shared_state.bot_status = f"PAUSED (WAITING {time_str})"
                             wait_time_s = 60 # Check again in 1 minute
                             logger.debug(f"[BUILD-M] Waiting for rolls... ({time_str})")
                        else:
                             shared_state.bot_status = "PAUSED (WAITING FOR RESOURCES)"
                             logger.debug(f"[BUILD-M] Waiting for rolls... (rolls={current_rolls})")
                        
                        sleep(wait_time_s)
                elif (
                    not shared_state.builder_running
                    and not self.should_start_building(rolls, money)
                ):  # Conditions not met, wait a bit and check again
                    wait_time_s = 2
                    if rolls < 5:
                        # Attempt to read the wait time from screen
                        time_str = self.check_wait_time()
                        if time_str:
                             shared_state.bot_status = f"PAUSED (WAITING {time_str})"
                             wait_time_s = 60 # Check again in 1 minute to update status
                             logger.debug(f"[BUILD-M] Waiting for rolls. Time remaining: {time_str}")
                        else:
                             shared_state.bot_status = "PAUSED (WAITING FOR RESOURCES)"
                             logger.debug(f"[BUILD-M] Conditions not met (rolls={rolls}, money={money}). Waiting...")
                    else:
                        logger.debug(f"[BUILD-M] Conditions not met (rolls={rolls}, money={money}). Waiting...")
                        
                    sleep(wait_time_s)  
                else:  # Builder is running, wait for it to finish
                    logger.debug("[BUILD-M] Builder is running, waiting...")
                    sleep(2)