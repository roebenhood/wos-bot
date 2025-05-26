import time
from config import SLEEP_TIME
from utils.adb_utils import PressBack, Tap
from utils.screen_utils import ExtractText, FindOnScreen, FindTemplate, FindWithRetries, GetScreenshot, ScreenHasText, WaitForImage
from utils import image_paths as img

def ClaimExplorationIdelRewards():
    btnClaim = FindWithRetries(lambda: FindOnScreen(img.btn_exploration_claim),)
    for attempt in range(3):
        if btnClaim:
            print(f"Exploration idle rewards claim button found. Tapping...")
            Tap(*btnClaim)
            screen = GetScreenshot()
            screen.show()
            rewardsClaimed = FindOnScreen(img.btn_exploration_claimed)
            if rewardsClaimed:
                print(f"Idle rewards already claimed")
                PressBack()
                return
            btnIdleIncom = WaitForImage(img.btn_exploration_idle_rewards)
            if btnIdleIncom:
                print(f"Idle income claim button found. Tapping...")
                Tap(*btnIdleIncom)
                PressBack()
                PressBack()
                return
            else:
                PressBack()
                return
        else:
            print(f"Claim rewards button not found.")
            attempt+1
            time.sleep(SLEEP_TIME)
    else:
        print(f"Claim rewards button not found after multiple attempts.")


    

