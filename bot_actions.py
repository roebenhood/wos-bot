import time
from config import MAX_ATTEMPTS, SLEEP_TIME
from utils.actions import ClearStack, SwitchView
from utils.adb_utils import PressBack, Swipe, Tap
from utils.screen_utils import CountMatches, FindAllTemplates, FindOnScreen, FindTemplate, GetScreenshot, ScreenHasText, TapWithRetry, WaitForImage
from utils import image_paths as img

def FarmResource(resource_key):
    actionType = ""
    targetType = ""
    if resource_key in ["meat","wood","coal","iron"]:
        actionType = targetType = "gather"
    elif resource_key == "polarTerror":
        actionType = "rally"
        targetType = "monster"
    elif resource_key == "beast":
        actionType = "attack"
        targetType = "monster"
    else:
        print(f"Resource key is unrecognized")
        return
    
    SwitchView("world")
    InitiateSearch()
    SearchResourceType(resource_key)
    SendTroops(actionType)
    DeployTroops(targetType)

def InitiateSearch():
    for attempt in range(5):
        screen = GetScreenshot()
        search_icon = FindTemplate(screen, img.btn_search_rss)
        if search_icon:
            print(f"Found search icon on attempt {attempt+1}, tapping...")
            Tap(*search_icon)
            time.sleep(SLEEP_TIME)
            break
        else:
            print(f"Search icon not found (attempt {attempt+1}). Retrying view reset...")
            SwitchView("world")
            time.sleep(SLEEP_TIME)
    else:
        print("Failed to find search icon after 5 attempts.")
        return
    
def SearchResourceType(resourceType: str):
    image_map = {
        "meat": img.rss_meat,
        "wood": img.rss_wood,
        "coal": img.rss_coal,
        "iron": img.rss_iron,
        "beast": img.rss_beast,
        "polarTerror": img.rss_polar_terror
    }

    # Step 3: Find the resource
    rssTemplatePath = image_map.get(resourceType)
    if not rssTemplatePath:
        print(f"Unknown resource: {resourceType}")
        return

    
    for attempt in range(MAX_ATTEMPTS + 1):
        rssTemplate = FindOnScreen(rssTemplatePath)
        
        if rssTemplate:
            print(f"Found {resourceType}, tapping...")
            Tap(*rssTemplate)
            time.sleep(SLEEP_TIME)
            break
        
        else:
            print(f"{resourceType} not found on screen (attempt {attempt+1}).")
            if attempt < MAX_ATTEMPTS // 2:
                print(f"Swiping RIGHT to LEFT to reveal more resources (attempt {attempt+1})")
                Swipe(500, 682, 200, 682, duration=500)

            else:
                print(f"Swiping LEFT to RIGHT to go back (attempt {attempt+1})")
                Swipe(200, 682, 500, 682, duration=500)
            time.sleep(SLEEP_TIME)

    btnGoSearch = FindOnScreen(img.btn_go_search)
    if btnGoSearch:
        print(f"Found search button, tapping...")
        Tap(*btnGoSearch)
        time.sleep(SLEEP_TIME)
    else:
        print(f"Search button not found on screen")
# Step 4: Set level of the resource

def SendTroops(actionType: str):
    if actionType == "monster":
        if TapWithRetry(img.btn_attack, "Attack button", retries=5):
            print("Monster attack started — now waiting for deploy screen...")
        else:
            print("Attack button not found.")
    elif actionType == "rally":
        TapWithRetry(img.btn_rally, "Rally button")
    elif actionType == "gather":
        TapWithRetry(img.btn_gather, "Gather button")
    elif actionType == "explore":
        TapWithRetry(img.btn_explore, "Explore button")
    elif actionType == "rescue":
        TapWithRetry(img.btn_rescue, "Rescue button")
    else:
        print(f"Unknown action type: {actionType}")



def DeployTroops(targetType: str):
    time.sleep(SLEEP_TIME)

    for attempt in range(3):
        if targetType == "gather":
            btnDeploy = FindOnScreen(img.btn_deploy_rss)
            if btnDeploy:
                Tap(*btnDeploy)
                print(f"Deploy button for gathering tapped (attempt {attempt+1})")
                return
            else:
                print(f"Deploy button for gather not found (attempt {attempt+1})")

        elif targetType == "monster":
            btnDeploy = FindOnScreen(img.btn_deploy_monster)
            if btnDeploy:
                Tap(*btnDeploy)
                print(f"Monster deploy button tapped (attempt {attempt+1})")
                return
            else:
                print(f"Monster deploy button not found (attempt {attempt+1})")

        elif targetType == "rally":
            btnHoldRally = FindOnScreen(img.btn_hold_rally)
            if btnHoldRally:
                Tap(*btnHoldRally)
                print(f"Hold a rally button tapped (attempt {attempt+1})")
                time.sleep(SLEEP_TIME)
                btnDeployRally = FindOnScreen(img.btn_deploy_monster)
                if btnDeployRally:
                    Tap(*btnDeployRally)
                    print(f"Rally deploy button tapped")
                    return
                else:
                    print("Rally deploy button not found after holding a rally.")
            else:
                print(f"Hold a rally button not found (attempt {attempt+1})")

        elif targetType == "explore":
            HandleExplorationAttack()
            return

        time.sleep(SLEEP_TIME)

    print("Failed to deploy troops after multiple attempts.")


def RunIntelTaskCycle():
    GoToIntelScreen()
    ClaimIntelRewards()

    while True:
        taskList = CheckIntelTasks()
        if not taskList:
            print("All intel tasks are completed.")
            break

        PerformIntelTasks(taskList)
        print("Claiming rewards after performing tasks...")
        ClaimIntelRewards()

    SwitchView("world")


# def CheckIntelTasks():
#     screen = GetScreenshot()
#     taskList = FindAllTemplates(screen, img.lh_tasks, threshold=0.7)

#     if not taskList:
#         print("No intel tasks found.")
#         return []

#     for task in taskList:
#         print(f"Found task: {task['type']} at {task['coords']}")
#     return taskList

def CheckIntelTasks(max_attempts=5, delay=0.3):
    for attempt in range(1, max_attempts + 1):
        screen = GetScreenshot()
        taskList = FindAllTemplates(screen, img.lh_tasks, threshold=0.85)

        if taskList:
            print(f"Tasks found on attempt {attempt}")
            for task in taskList:
                print(f"Found task: {task['type']} at {task['coords']}")
            return taskList
        else:
            print(f"No tasks found (attempt {attempt}), retrying...")
            time.sleep(delay)

    print("📭 No intel tasks found after multiple attempts.")
    return []


def PerformIntelTasks(taskList):
    for task in taskList:
        x, y = task['coords']
        Tap(x, y)
        time.sleep(SLEEP_TIME)

        for findAttempt in range(1, 4):
            btnView = FindOnScreen(img.lh_btn_view)
            if btnView:
                print(f"View task button found on attempt {findAttempt}, tapping...")
                Tap(*btnView)
                time.sleep(5)

                SendTroops(task['type'])
                time.sleep(SLEEP_TIME)

                print(f"Task type: {task['type']}")
                DeployTroops(task['type'])
                time.sleep(SLEEP_TIME)

                # Always return to Intel screen after deploy
                GoToIntelScreen()
                break
            else:
                print(f"View button not found (attempt {findAttempt})")
                keywords = ["victory", "rewards", "exit", "anywhere", "marching"]
                if ScreenHasText(keywords):
                    PressBack()
                time.sleep(SLEEP_TIME)
        else:
            GoToIntelScreen()

        time.sleep(SLEEP_TIME)



def ClaimIntelRewards():
    for attempt in range(MAX_ATTEMPTS):
        if not FindOnScreen(img.screen_intel):
            GoToIntelScreen()

        claimCount = CountMatches(GetScreenshot(), img.lh_claim)
        if claimCount == 0:
            print("No tasks to claim.")
            break

        print(f"Claimable tasks: {claimCount}")
        for _ in range(claimCount):
            claimBtn = FindOnScreen(img.lh_claim)
            if claimBtn:
                Tap(*claimBtn)
                time.sleep(SLEEP_TIME)
                PressBack()
                print(f"Pressed back")
                time.sleep(SLEEP_TIME)
                break


def GoToIntelScreen():
    if FindOnScreen(img.screen_intel):
        return

    for attempt in range(MAX_ATTEMPTS):
        btnIntel = FindOnScreen(img.btn_lighthouse)
        if btnIntel:
            print(f"Going to Intel screen (attempt {attempt + 1})")
            Tap(*btnIntel)
            time.sleep(SLEEP_TIME)
            return
        else:
            print(f"🔄 Lighthouse not found (attempt {attempt + 1}), resetting view...")
            SwitchView("world")
            time.sleep(SLEEP_TIME)



def HandleExplorationAttack():

    for attempt in range(MAX_ATTEMPTS):
        screen = GetScreenshot()
        btnQuickDeploy = FindTemplate(screen, img.btn_quick_deploy)
        btnFight = FindTemplate(screen, img.btn_explore_fight)
        if btnFight and btnQuickDeploy:
            print(f"Exploration buttons found on {attempt} attempts.")
            print(f"Tapping Quick Deploy button")
            Tap(*btnQuickDeploy)
            time.sleep(SLEEP_TIME)
            print(f"Tapping Fight button")
            Tap(*btnFight)            
            print(f"Waiting for the match to end")
            battleResult = WaitForImage(img.msg_tap_to_exit)
            Tap(*battleResult)
            time.sleep(SLEEP_TIME)
            return
        else:
            print(f"Fight button not found.")
    else:
        print("Failed to find search icon after 5 attempts.")
        return




