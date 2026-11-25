import os
import subprocess
import time
import pyautogui
import webbrowser
import pygetwindow as gw

# ==============================================================================
# Multi-Monitor AI Workspace Automation Script (Windows)
# Launches ComfyUI, prompt scratchpad, and arranges tabbed File Explorer
# windows across primary and secondary displays automatically.
# ==============================================================================

# ==================== CONFIGURATION ====================
PRIMARY_MONITOR_WIDTH = 1920  # Set to primary display horizontal resolution

PROMPT_NOTES_FILE = r"./notes/prompt_templates.txt"
COMFYUI_START_BAT = r"./ComfyUI/start_comfyui.bat"
REFERENCE_URL = "https://google.com"
BROWSER_PATH = r"C:/Program Files/Mozilla Firefox/firefox.exe"

# Window 1: Models, Datasets & Training Outputs (Secondary Monitor)
WINDOW_1_TABS = [
    r"./AI-Toolkit/output",
    r"./AI-Toolkit/datasets",
    r"./ComfyUI/models/loras",
    r"./ComfyUI/input/DataSetFLUX",
    r"./ComfyUI/input/DataSetPONY",
]

# Window 2: Render Outputs & Post-Processing (Secondary Monitor)
WINDOW_2_TABS = [
    r"./ComfyUI/output/Photo",
    r"./ComfyUI/output/FLUX/ADetailer",
    r"./ComfyUI/output/Video",
]

ACTION_DELAY = 0.8
# =======================================================


def open_tabbed_explorer(folder_list, x, y, width=None, height=None, maximize=False):
    """Opens Windows File Explorer, positions it on target display, and opens tabs."""
    if not folder_list:
        return

    existing_windows = gw.getWindowsWithTitle("File Explorer")
    subprocess.Popen(f'explorer "{os.path.abspath(folder_list[0])}"', shell=True)
    time.sleep(ACTION_DELAY + 1.2)

    current_windows = gw.getWindowsWithTitle("File Explorer")
    new_windows = [w for w in current_windows if w not in existing_windows]

    if new_windows:
        win = new_windows[0]
        if win.isMaximized:
            win.restore()

        win.moveTo(x, y)
        time.sleep(0.2)

        if maximize:
            win.maximize()
        elif width and height:
            win.resizeTo(width, height)

        win.activate()
        time.sleep(0.3)

    for folder in folder_list[1:]:
        pyautogui.hotkey("ctrl", "t")
        time.sleep(0.4)
        pyautogui.hotkey("alt", "d")
        time.sleep(0.2)
        pyautogui.write(os.path.abspath(folder))
        pyautogui.press("enter")
        time.sleep(ACTION_DELAY)


def main():
    print("Initializing Multi-Monitor AI Workspace...")

    if os.path.exists(PROMPT_NOTES_FILE):
        subprocess.Popen(["notepad.exe", PROMPT_NOTES_FILE])
        time.sleep(ACTION_DELAY)

    if os.path.exists(COMFYUI_START_BAT):
        bat_dir = os.path.dirname(os.path.abspath(COMFYUI_START_BAT))
        subprocess.Popen(f'start cmd /k "{os.path.basename(COMFYUI_START_BAT)}"', cwd=bat_dir, shell=True)
        time.sleep(ACTION_DELAY)

    if os.path.exists(BROWSER_PATH):
        webbrowser.register("custom_browser", None, webbrowser.BackgroundBrowser(BROWSER_PATH))
        webbrowser.get("custom_browser").open(REFERENCE_URL)
        time.sleep(ACTION_DELAY + 0.5)

    secondary_x = PRIMARY_MONITOR_WIDTH + 10
    secondary_y = 10

    open_tabbed_explorer(WINDOW_1_TABS, x=secondary_x, y=secondary_y, maximize=True)
    open_tabbed_explorer(WINDOW_2_TABS, x=secondary_x, y=secondary_y, maximize=True)

    print("Workspace restored successfully.")


if __name__ == "__main__":
    main()