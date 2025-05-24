import time
from config import MAX_ATTEMPTS, SLEEP_TIME
from utils.actions import ClearStack, SwitchView
from utils.adb_utils import PressBack, Swipe, Tap
from utils.screen_utils import CountMatches, FindAllTemplates, FindOnScreen, FindTemplate, GetScreenshot, WaitForImage
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
    # Types: attack, rally, gather, explore, rescue
    # Step 6: Click gather or attack
    if actionType == "monster":
        for attempt in range(5):
            btnAttack = FindOnScreen(img.btn_attack)
            if btnAttack:
                print(f"Found attack button on attempt {attempt+1}, tapping...")
                Tap(*btnAttack)
                time.sleep(SLEEP_TIME)
                break
            else:
                print(f"Attack button not found (attempt {attempt+1}). Retrying...")
                time.sleep(SLEEP_TIME)
        else:
            print("Failed to find search icon after 5 attempts.")
            return
        for attempt in range(3):
            btnAttack = FindOnScreen(img.btn_attack)
            if btnAttack:
                Tap(*btnAttack)
                print(f"Attack button found")
            else:
                btnAttackGo = FindOnScreen(img.btn_attack_go)
                if btnAttackGo:
                    Tap(*btnAttackGo)
                    print(f"Attack button found but will attack lower level first")
                    return 0
                else:
                    print(f"Attack button not found")
                    return 0
    elif actionType == "rally":
        btnRally = FindOnScreen(img.btn_rally)
        if btnRally:
            # Step 1: Select rally timer
            # Step 2: Tap 'Hold a rally' button
            # Step 3: Deploy
            print(f"Rally button found")
        else:
            print(f"Rally button not found")
            return 0
    elif actionType == "gather":
        btnGather = FindOnScreen(img.btn_gather)
        if btnGather:
            Tap(*btnGather)
            print(f"Gather button found")
            return
        else:
            print(f"Gather button not found")
            return 0
    elif actionType == "explore":
        btnExplore = FindOnScreen(img.btn_explore)
        if btnExplore:
            Tap(*btnExplore)
            print(f"Explore button found")
            return
        else:
            print(f"Explore button not found")
            return 0
    elif actionType == "rescue":
        btnRescue = FindOnScreen(img.btn_rescue)
        if btnRescue:
            print(f"Rescue button found")
            return
        else:
            print(f"Rescue button not found")
            return 0
    else:
        print(f"No button found")
        return 0

def DeployTroops(targetType: str):
    # Target types: gather, monster 
    time.sleep(SLEEP_TIME)
    for attempt in range(3):
        if targetType == "gather":
            btnDeployRss = FindOnScreen(img.btn_deploy_rss)
            if btnDeployRss:
                Tap(*btnDeployRss)
                print(f"Deploy button for gathering found on attempt {attempt+1}, tapping...")
                break
            else:
                print(f"Deploy button for gathering not found. (attempt {attempt+1}). Retrying...")
                time.sleep(SLEEP_TIME)
        elif targetType == "explore":
            btnFight = FindOnScreen(img.btn_explore_fight)
            if btnFight:
                Tap(*btnFight)
                print(f"Fight button found")
                print(f"Waiting for the match to end")
                battleResult = WaitForImage(img.msg_tap_to_exit)
                Tap(*battleResult)
                return
            else:
                print(f"Fight button not found.")
        elif targetType == "monster":
            btnDeployMonster = FindOnScreen(img.btn_deploy_monster)
            if btnDeployMonster:
                Tap(*btnDeployMonster)
                print(f"Deploy button for monster found")
            else:
                print(f"Deploy button for monster not found. (attempt {attempt+1}). Retrying...")
    else:
        print("Failed to find deploy button after 3 attempts.")
        return
    
def CheckIntelTasks():
    screen = GetScreenshot()
    taskList = FindAllTemplates(screen, img.lh_tasks)
    for intelTask in taskList:
        print(f"Found task: {intelTask['type']} at {intelTask['coords']}")

    for task in taskList:
        x,y = task['coords']
        Tap(x,y)
        time.sleep(SLEEP_TIME)
        for findAttempt in range(1, 3 + 1):
            btnView = FindOnScreen(img.lh_btn_view)
            if btnView:
                print(f"View task button found on attempt {findAttempt}, tapping...")
                Tap(*btnView)
                time.sleep(5)
                SendTroops(task['type'])
                time.sleep(SLEEP_TIME)
                DeployTroops(task['type'])
                time.sleep(SLEEP_TIME)
            else:
                print(f"View button not found (attempt {findAttempt})")
                time.sleep(SLEEP_TIME)
        time.sleep(SLEEP_TIME)

    


def ClaimIntelRewards():
    screen = GetScreenshot()
    claimCount = CountMatches(screen, img.lh_claim)
    print(f"Tasks claimable: {claimCount}")
    for attempt in range(claimCount):
        lhClaim = FindOnScreen(img.lh_claim)
        if lhClaim:
            Tap(*lhClaim)
            time.sleep(SLEEP_TIME)
            PressBack()
            time.sleep(SLEEP_TIME)
    else:
        print(f"No tasks to claim")

def HandleExplorationAttack(explorationType: str):
    # Step 0: Determin if this attack is in exploration or from lighthouse attack
    # Step 1: Make sure to use the best heroes
    # Step 2: Click Fight button to initiate fight
    # Step 3: Wait for the match to end
    # Step 4: Close the victory pop-up screen (click anywhare to exit)

    btns_exploration = {
    "btnQuickDeploy": img.btn_explore_quick_deploy,
    "btnFight": img.btn_explore_fight
    }
    for attempt in range(MAX_ATTEMPTS):
        btnFight = FindAllTemplates(GetScreenshot(), btns_exploration)
        if btnFight:
            Tap(*btnFight)
            print(f"Fight button found")
            print(f"Waiting for the match to end")
            battleResult = WaitForImage(img.msg_tap_to_exit)
            Tap(*battleResult)
            return
        else:
            print(f"Fight button not found.")
    else:
        print("Failed to find search icon after 5 attempts.")
        return




