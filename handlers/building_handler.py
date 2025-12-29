"""
building_handler.py

This module contains the BuildingHandler class, which is responsible for handling building upgrades. It is called by the building_monitor.py and runs in a separate thread.
It is responsible for:
    - Entering the build menu
    - OCR to get the cost of each building upgrade
    - Upgrading buildings
    - Gathering data about each board
"""

from shared_state import shared_state
from pyautogui import moveTo
from pydirectinput import click
from time import sleep
import re
from utils.ocr_utils import OCRUtils
import os
import json
from utils.logger import logger

ocr_utils = OCRUtils()


class BuildingHandler:
    """
    The BuildingHandler class manages building-related operations in the game.

    Attributes:
        current_path (str): The current working directory.
        game_data_file (str): The name of the game data file (JSON format).
        current_money (int): The current amount of in-game currency.
        window_x (int): The x-coordinate of the game window.
        window_y (int): The y-coordinate of the game window.
        window_width (int): The width of the game window.
        window_height (int): The height of the game window.
        current_board_data (dict): Data for the current game board.
        buildings (list): A list of dictionaries containing building information.
        data (list): A list containing game data.

    Methods:
        __init__(self):
            Initializes a BuildingHandler object.

        load_data(self):
            Loads game data from the game_data_file.

        save_data(self):
            Batch saves game data to the game_data_file.

        process_board_name(self, board_name):
            Processes board name from OCR results.

        gather_board_name(self):
            Retrieves the game board name using OCR.

        enter_build_menu(self):
            Navigates to the game's build menu.

        check_menu_status(self):
            Checks if the game is in the build menu.

        extract_and_convert_cost(self, cost_text):
            Extracts and converts building costs from OCR results.

        gather_board_number(self):
            Retrieves the board number for the current game board.

        find_max_board_number(self):
            Finds the maximum board number in the game data.

        create_new_board(self):
            Creates a new game board entry.

        update_and_append_board_data(self):
            Updates and appends board data to the game data.

        exit_build_menu(self):
            Exits the game's build menu.

        run(self):
            Main method that manages the building process in the game.
    """

    def __init__(self):
        # Establish current path and game data file
        self.current_path = shared_state.current_path
        self.game_data_file = str(shared_state.WINDOW_TITLE.strip()) + "_game_data.json"
        # Wait for money to update
        with shared_state.money_condition:
            shared_state.money_condition.wait()
        self.all_buildings_upgraded = False
        shared_state.builder_finished = False
        self.current_money = shared_state.money
        self.minimum_money_to_continue = 1000  # Denaro minimo per continuare a costruire
        # Initialize window coordinates
        (
            self.window_x,
            self.window_y,
            self.window_width,
            self.window_height,
        ) = shared_state.window
        # Initialize current_board_data
        self.current_board_data = {}
        self.buildings = [
            {
                "name": "building1",
                "x_percent": 37,
                "y_percent": 86,
                "right_percent": 40.5,
                "bottom_percent": 91,
                "upgrade_level": 0,
                "upgrade0": 0,
                "upgrade1": 0,
                "upgrade2": 0,
                "upgrade3": 0,
                "upgrade4": 0,
                "upgrade5": 0,
                "upgrade6": 0,
            },
            {
                "name": "building2",
                "x_percent": 42.5,
                "y_percent": 86,
                "right_percent": 46,
                "bottom_percent": 91,
                "upgrade_level": 0,
                "upgrade0": 0,
                "upgrade1": 0,
                "upgrade2": 0,
                "upgrade3": 0,
                "upgrade4": 0,
                "upgrade5": 0,
                "upgrade6": 0,
            },
            {
                "name": "building3",
                "x_percent": 48.5,
                "y_percent": 86,
                "right_percent": 52,
                "bottom_percent": 91,
                "upgrade_level": 0,
                "upgrade0": 0,
                "upgrade1": 0,
                "upgrade2": 0,
                "upgrade3": 0,
                "upgrade4": 0,
                "upgrade5": 0,
                "upgrade6": 0,
            },
            {
                "name": "building4",
                "x_percent": 54.5,
                "y_percent": 86,
                "right_percent": 58,
                "bottom_percent": 91,
                "upgrade_level": 0,
                "upgrade0": 0,
                "upgrade1": 0,
                "upgrade2": 0,
                "upgrade3": 0,
                "upgrade4": 0,
                "upgrade5": 0,
                "upgrade6": 0,
            },
            {
                "name": "building5",
                "x_percent": 60.5,
                "y_percent": 86,
                "right_percent": 64,
                "bottom_percent": 91,
                "upgrade_level": 0,
                "upgrade0": 0,
                "upgrade1": 0,
                "upgrade2": 0,
                "upgrade3": 0,
                "upgrade4": 0,
                "upgrade5": 0,
                "upgrade6": 0,
            },
        ]
        self.data = self.load_data()

        logger.debug("[BUILDER] Initialized successfully.")

    def load_data(self):
        """
        Loads game data from the game_data_file.

        Returns:
            list: A list containing game data.
        """
        try:
            with open(self.game_data_file, "r") as f:
                logger.debug(f"[BUILDER] Loaded data from {self.game_data_file}.")
                return json.load(f)

        except FileNotFoundError:
            logger.error("[BUILDER] game_data.json not found.")
            return []

    def save_data(self):
        """
        Batch saves game data to the game_data_file.
        """
        logger.debug(f"[BUILDER] Saving data to {self.game_data_file}...")
        with open(self.game_data_file, "w") as f:
            json.dump(self.data, f, indent=4)
        # logger.debug(f"[BUILDER] Saved data: {self.data}.")

    def process_board_name(self, board_name):
        """
        Processes board name from OCR results.
        """
        pattern = r"\d+/30"  # Matches the progress of building upgrades
        cleaned_name = re.sub(
            r"[^a-zA-Z0-9/ ]", "", board_name
        )  # Remove all non-alphanumeric characters except for "/" and " "
        match = re.search(pattern, cleaned_name)
        if match:
            start, _ = match.span()
            extracted_text = board_name[
                :start
            ].strip()  # Remove the progress of building upgrades
            return extracted_text
        else:
            return board_name

    def gather_board_name(self):
        """
        Retrieves the game board name using OCR.
        """
        board_name_region = (1, 91.7, 94.9, 95)
        board_x_percent = board_name_region[0]
        board_y_percent = board_name_region[1]
        board_right_percent = board_name_region[2]
        board_bottom_percent = board_name_region[3]
        board_process_settings = {
            "contrast_reduction_percentage": 0,
            "threshold_value": 75,
            "invert": False,
            "scale_factor": 4,
        }
        board_name = None
        board_name = ocr_utils.ocr_to_str(
            board_x_percent,
            board_y_percent,
            board_right_percent,
            board_bottom_percent,
            ocr_settings="--psm 7 --oem 3 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789/ ",
            process_settings=board_process_settings,
        )
        board_name_proc = self.process_board_name(board_name)
        logger.debug(f"[BUILDER] Board name is {board_name_proc}.")
        return board_name_proc

    def enter_build_menu(self):
        """
        Navigates to the game's build menu.
        When called, will loop until the game is in the build menu.
        """
        in_menu = self.check_menu_status()
        print(in_menu)
        while not in_menu:
            in_menu = self.check_menu_status()
            print(in_menu)
            if not in_menu:
                logger.debug("[BUILDER] Not in menu, looking for build icon")
                build_path = os.path.join(self.current_path, "images", "build.png")
                build_image = shared_state.load_image(build_path)
                location = ocr_utils.find(build_image)
                if location:
                    logger.debug(f"[BUILDER] Found build menu icon at {location}. Clicking...")
                    x, y = location
                    with shared_state.moveTo_lock:
                        moveTo(x, y)
                        sleep(0.2)
                        click()
                    sleep(2)
                    in_menu = self.check_menu_status()
                    print(in_menu)
                else:
                    logger.debug("[BUILDER] Build icon not found, waiting...")
                    sleep(1)

    def check_menu_status(self):
        """
        When called, will check if the game is in the build menu.
        Returns:
            bool: True if the game is in the build menu, False otherwise.
        """
        exit_path = os.path.join(self.current_path, "images", "build-exit.png")
        exit_image = shared_state.load_image(exit_path)
        location = ocr_utils.find(exit_image)
        if not location:
            # logger.debug("[BUILDER] Not in build menu.")
            return False
        if location:
            # logger.debug("[BUILDER] In build menu.")
            return True

    def extract_and_convert_cost(self, cost_text):
        """
        Extracts and converts building costs from OCR results.
        Returns:
            int: The cost of the building upgrade.
        """
        logger.debug(f"[BUILD-H] Extracting cost from OCR text: '{cost_text}'")
        pattern = r"(\d+(\.\d+)?)([MK]?)"  # Matches numbers with optional decimal point and optional "M" or "K" at the end
        match = re.search(pattern, cost_text)
        if match:
            numeric_part, decimal_part, unit_part = match.groups()
            if not unit_part and decimal_part:
                # Numeric part has a decimal point but no "M" or "K"
                conversion_factor = 1000
            else:
                conversion_factor = (
                    1_000_000
                    if unit_part == "M"
                    else (1_000 if unit_part == "K" else 1)
                )
            numeric_part = numeric_part.replace(
                ",", ""
            )  # Remove commas as digit separators
            self.cost_value = int(float(numeric_part) * conversion_factor)
            logger.debug(f"[BUILD-H] Converted '{cost_text}' -> {self.cost_value:,}")
            return self.cost_value
        else:
            logger.debug(f"[BUILD-H] Failed to parse cost from '{cost_text}', returning 0")
            return 0

    def gather_board_number(self):
        """
        Retrieves the board number for the current game board if the board number exists in the current game data.
        Returns:
            int: The board number for the current game board.
        """
        active_board_name = self.gather_board_name()
        for board_data in self.data:
            if board_data["board_name"] == active_board_name:
                return board_data["board_number"]
        return None

    def find_max_board_number(self):
        """
        Finds the maximum board number in the game data.
        Returns:
            int: The maximum board number in the game data.
        """
        max_board_number = 0
        for board_data in self.data:
            board_number = board_data.get("board_number", 0)
            max_board_number = max(max_board_number, board_number)
        return max_board_number

    def create_new_board(self):
        """
        Creates a new game board entry.
        Returns:
            dict: A dictionary containing the new game board data.
        """
        if self.board_number is not None:
            new_board_number = self.board_number + 1
        else:
            # Get the maximum board number from existing data and increment it by 1
            new_board_number = self.find_max_board_number() + 1

        new_board_name = self.board_name
        new_board_data = {
            "board_number": new_board_number,
            "board_name": new_board_name,
            "building1": [0, 0, 0, 0, 0, 0],
            "building2": [0, 0, 0, 0, 0, 0],
            "building3": [0, 0, 0, 0, 0, 0],
            "building4": [0, 0, 0, 0, 0, 0],
            "building5": [0, 0, 0, 0, 0, 0],
        }
        # logger.debug(f"[BUILDER] Created a new board: {new_board_data}")
        return new_board_data

    def update_and_append_board_data(self):
        """
        Updates and appends board data to the game data.
        If board name exists in game data, update the existing entry.
        If board name does not exist in game data, append a new entry.
        """
        found_board = False
        for board_data in self.data:
            if board_data["board_name"] == self.board_name:
                # Merge the building data into the existing board_data
                for building_info in self.buildings:
                    building_name = building_info["name"]
                    upgrades = [building_info[f"upgrade{i}"] for i in range(6)]
                    board_data[building_name] = upgrades
                found_board = True
                # logger.debug(f"[BUILDER] Updated board_data: {board_data}")
                break

        if not found_board:
            # If the board name doesn't exist in self.data, add a new entry
            new_board_data = self.create_new_board()
            for building_info in self.buildings:
                building_name = building_info["name"]
                upgrades = [building_info[f"upgrade{i}"] for i in range(6)]
                new_board_data[building_name] = upgrades
            self.data.append(new_board_data)
            # logger.debug(f"[BUILDER] Appended new board_data: {new_board_data}")

    def calculate_total_cost(self):
        """
        Calculate the total cost of all building upgrades on the current board.
        """
        total_cost = 0
        for building_info in self.buildings:
            building_name = building_info["name"]
            upgrades = [
                building_info[f"upgrade{i}"] for i in range(6)
            ]  # Get upgrade costs
            total_cost += sum(upgrades)  # Sum the upgrade costs for this building
        return total_cost

    def update_total_cost_in_json(self):
        """
        Update the JSON data with the total cost of the current board.
        """
        board_name = self.board_name
        total_cost = self.calculate_total_cost()

        # Iterate through the existing data to find the board by name
        for board_data in self.data:
            if board_data["board_name"] == board_name:
                board_data["total_cost"] = total_cost
                break  # Exit the loop after updating the data

        # Save the updated data to the JSON file
        self.save_data()

    def has_enough_money_to_continue(self):
        """
        Verifica se c'è ancora abbastanza denaro per continuare a costruire.
        Returns:
            bool: True se c'è abbastanza denaro, False altrimenti
        """
        with shared_state.money_condition:
            shared_state.money_condition.wait()
        self.current_money = shared_state.money
        return self.current_money >= self.minimum_money_to_continue

    def exit_build_menu(self):
        """
        Exits the game's build menu.
        Currently not used, as when a board is finished, the game automatically exits the build menu.
        """
        in_menu = self.check_menu_status()
        print(in_menu)
        if in_menu:
            build_exit_path = os.path.join(
                self.current_path, "images", "build-exit.png"
            )
            build_exit_image = shared_state.load_image(build_exit_path)
            in_menu = self.check_menu_status()
            print(in_menu)
            while in_menu:
                location = ocr_utils.find(build_exit_image)
                logger.debug("[BUILDER] Exiting build menu...")
                if location:
                    with shared_state.moveTo_lock:
                        moveTo(location)
                        sleep(0.5)
                        click()
                    sleep(2)
                if not location:
                    logger.debug("[BUILDER] Exited build menu successfully...")
                    break
                break
            with shared_state.builder_finished_condition:
                shared_state.builder_finished_condition.notify_all()
        else:
            with shared_state.builder_finished_condition:
                shared_state.builder_finished_condition.notify_all()

    def run(self):
        """
        Main method that manages the building process in the game.
        Exits upon completing all building upgrades or encountering 3 consecutive UI popups.
        """
        building_finished_path = os.path.join(
            self.current_path, "images", "building-finished.png"
        )
        building_finished_image = shared_state.load_image(building_finished_path)
        
        in_menu = self.check_menu_status()
        if not in_menu:
            self.enter_build_menu()
            
        with shared_state.builder_running_condition:
            shared_state.builder_running_condition.wait_for(
                lambda: shared_state.builder_running
            )
            
        consecutive_popups = 0
        
        while True:
            # Check exit condition based on popups
            if consecutive_popups >= 3:
                logger.debug("[BUILDER] 3 Consecutive UI popups detected. Assuming money is spent. Exiting...")
                break
                
            self.board_name = self.gather_board_name()
            # If board name invalid, try to re-enter or continue
            
            # Update Money from shared state
            with shared_state.money_condition:
                if shared_state.money is not None:
                    self.current_money = shared_state.money
                
            # Iterate through buildings
            actions_taken_in_this_cycle = 0
            
            for building_info in self.buildings:
                # Check popup limit immediately
                if consecutive_popups >= 3:
                    break
                    
                # Ensure we are in menu
                if not self.check_menu_status():
                    logger.debug("[BUILDER] Lost menu focus, trying to re-enter...")
                    self.enter_build_menu()
                
                building_name = building_info["name"]
                x_percent = building_info["x_percent"]
                y_percent = building_info["y_percent"]
                right_percent = building_info["right_percent"]
                bottom_percent = building_info["bottom_percent"]
                
                # Calculate coordinates
                self.x = int(self.window_x + (self.window_width * (x_percent / 100)))
                self.y = int(self.window_y + (self.window_height * (y_percent / 100)))
                self.right = int(self.window_x + (self.window_width * (right_percent / 100)))
                self.bottom = int(self.window_y + (self.window_height * (bottom_percent / 100)))
                
                # Attempt OCR
                ocr_settings = r"--psm 7 --oem 3 -c tessedit_char_whitelist=0123456789.MK"
                process_settings = {"threshold_value": 100, "invert": True, "scale_factor": 3}
                
                cost_text = ocr_utils.ocr_to_str(
                    x_percent, y_percent, right_percent, bottom_percent,
                    ocr_settings=ocr_settings,
                    process_settings=process_settings
                )
                cost = self.extract_and_convert_cost(cost_text)
                
                should_click = False
                
                if cost > 0:
                    # Valid cost detected
                    if self.current_money >= cost:
                        logger.debug(f"[BUILDER] Cost {cost} <= Money {self.current_money}. Clicking {building_name}...")
                        should_click = True
                    else:
                        logger.debug(f"[BUILDER] Cost {cost} > Money {self.current_money}. Skipping {building_name}.")
                        should_click = False
                else:
                    # Invalid/Unknown cost -> Blind Click
                    logger.debug(f"[BUILDER] Cost unknown for {building_name}. Blind clicking...")
                    should_click = True
                
                if should_click:
                    with shared_state.moveTo_lock:
                        moveTo(self.x, self.y)
                        click()
                    actions_taken_in_this_cycle += 1
                    sleep(1.5) # Wait for animation/potential popup
                    
                    # Check for popup
                    # We need to check if the UI handler flagged a popup
                    popup_detected = False
                    with shared_state.ui_condition:
                        if shared_state.popup_handled:
                            popup_detected = True
                            shared_state.popup_handled = False # Reset
                    
                    if popup_detected:
                        consecutive_popups += 1
                        logger.debug(f"[BUILDER] Popup detected! Consecutive count: {consecutive_popups}")
                    else:
                        consecutive_popups = 0 # Reset on success/no-popup
                        
                    # Update money after action
                    with shared_state.money_condition:
                        shared_state.money_condition.wait(timeout=0.5)
                        self.current_money = shared_state.money if shared_state.money is not None else self.current_money
                else:
                    sleep(0.1)

            # If we cycled through all buildings and didn't click anything (because we knew we had no money), exit
            if actions_taken_in_this_cycle == 0 and consecutive_popups < 3:
                # Double check money logic? 
                # If we skipped everything because Money < Cost, we are done.
                logger.debug("[BUILDER] No actions taken in this cycle (Money insufficient for known costs). Exiting...")
                break
                
            sleep(1) 

        # Cleanup and Exit
        logger.debug("[BUILDER] Exiting building handler...")
        self.save_data()
        self.exit_build_menu() # Try to exit gracefully
        with shared_state.builder_finished_condition:
            shared_state.builder_finished = True
            shared_state.builder_finished_condition.notify_all()
