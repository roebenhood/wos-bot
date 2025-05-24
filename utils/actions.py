
from utils.adb_utils import PressBack, Tap
from utils import image_paths as img
from config import SLEEP_TIME, MAX_ATTEMPTS
import time

from utils.screen_utils import FindTemplate, GetScreenshot, WaitForImage

def ClearStack():
    """
    Presses back repeatedly until the quit dialog is detected.
    Then taps the cancel button if found.
    """
    attempt = 1
    while True:
        screen = GetScreenshot()
        if screen is None:
            print("Screenshot failed.")
            return

        quit_dialog = FindTemplate(screen, img.dialog_quit)
        if quit_dialog:
            cancel_coords = FindTemplate(screen, img.btn_cancel)
            if cancel_coords:
                Tap(*cancel_coords)
            else:
                print("Cancel button not found.")
            break
        else:
            print(f"No quit dialog (attempt {attempt}). Pressing back...")
            PressBack()
            time.sleep(2)
            attempt += 1
    return


def GetCurrentView(current_screen):
    world_coords = FindTemplate(current_screen, img.btn_world)
    if world_coords:
        return world_coords, "city"

    city_coords = FindTemplate(current_screen, img.btn_city)
    if city_coords:
        return city_coords, "world"

    return None, None

def SwitchView(target_view: str, max_retries: int = 3):
    """
    Switches to the specified view: 'city' or 'world'.
    Detects current view and taps the corresponding switch button if needed.
    Retries if the switch button is not found.
    """
    for attempt in range(1, max_retries + 1):
        print(f"Attempt {attempt} to switch to {target_view} view...")
        screen = GetScreenshot()
        coords, current_view = GetCurrentView(screen)

        if current_view == target_view:
            print(f"Already in {target_view} view.")
            return

        if coords:
            print(f"Switching to {target_view} view...")
            Tap(*coords)

            expected_image = img.btn_city if target_view == "world" else img.btn_world
            result = WaitForImage(expected_image)

            if result:
                print(f"Now in {target_view} view.")
                return
            else:
                print(f"Timeout waiting for {target_view} view to load.")
        else:
            print("Could not find view switch button.")
            ClearStack()
    
    print(f"Failed to switch to {target_view} view after {max_retries} attempts.")
