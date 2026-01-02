import pygetwindow as gw
# import inquirer
import subprocess
import sys
import time
import os

def get_bluestacks_windows():
    """Detects all visible BlueStacks windows."""
    windows = gw.getAllTitles()
    bs_windows = [w for w in windows if "BlueStacks" in w and w.strip()]
    return list(set(bs_windows))  # Deduplicate

def main():
    print("Searching for BlueStacks windows...")
    bs_windows = get_bluestacks_windows()

    if not bs_windows:
        print("No BlueStacks windows found! Make sure they are open and visible.")
        input("Press Enter to exit...")
        return

    print("\nAvailable BlueStacks Windows:")
    print("0) [ALL WINDOWS]")
    for i, window in enumerate(bs_windows):
        print(f"{i+1}) {window}")

    print("\nEnter the numbers of the windows you want to start (comma separated, e.g. 1,3)")
    print("Or type '0' or 'all' for all windows.")
    
    selected_indices = []
    while True:
        try:
            user_input = input("Selection: ").strip().lower()
            if not user_input:
                continue
            
            if user_input == '0' or user_input == 'all':
                target_windows = bs_windows
                break

            parts = user_input.split(',')
            valid_selection = True
            
            current_selection = []
            for part in parts:
                part = part.strip()
                if not part: continue
                idx = int(part) - 1
                if 0 <= idx < len(bs_windows):
                    current_selection.append(bs_windows[idx])
                else:
                    print(f"Invalid selection: {part}")
                    valid_selection = False
            
            if valid_selection and current_selection:
                target_windows = current_selection
                break
            else:
                print("Please try again.")

        except ValueError:
            print("Invalid input. Please enter numbers.")

    processes = []
    print(f"\nStarting bots for windows: {', '.join(target_windows)}")
    
    # Get python executable
    python_exe = sys.executable

    for window_title in target_windows:
        print(f"Launching bot for: {window_title}")
        # Launch main.py in a new separate console window for each bot
        # Use cmd /k to keep window open if it crashes
        # "start" command in shell is another way, but Popen with creationflags is cleaner for Python
        # We wrap the command in cmd.exe /K
        cmd = ["cmd.exe", "/K", python_exe, "main.py", "--window", window_title]
        
        try:
            p = subprocess.Popen(cmd, creationflags=subprocess.CREATE_NEW_CONSOLE)
            processes.append(p)
            time.sleep(2) # Stagger start to avoid initial CPU spike
        except Exception as e:
            print(f"Failed to start bot for {window_title}: {e}")

    print(f"\nStarted {len(processes)} bots.")
    print("Press Ctrl+C to close this launcher (bots will continue running).")
    
    try:
        while True:
            time.sleep(1)
            # Optional: Check if processes are still alive needed? 
            # If we want the launcher to keep running, we loop.
    except KeyboardInterrupt:
        print("Exiting launcher.")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"An error occurred: {e}")
        input("Press Enter to exit...")
