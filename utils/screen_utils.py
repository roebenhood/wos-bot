import subprocess
import time
from PIL import Image
import io
import cv2
import numpy as np
import pytesseract
from PIL import Image
from utils import image_paths as img

from config import DEVICE_ID, SLEEP_TIME, WAIT_POLL, WAIT_TIMEOUT
from utils.adb_utils import PressBack, Tap

device_id = DEVICE_ID

def GetScreenshot():
    result = subprocess.run(['adb', '-s', device_id, 'exec-out', 'screencap', '-p'], capture_output=True)
    return Image.open(io.BytesIO(result.stdout))

def GetScreenshotCV():
    result = subprocess.run(['adb', 'exec-out', 'screencap', '-p'], capture_output=True)
    image = Image.open(io.BytesIO(result.stdout))
    return cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

def FindTemplate(screen_img, template_path, threshold=0.8):
    if screen_img is None:
        print(f"No screenshot.")
        return None
    
    template = cv2.imread(template_path, cv2.IMREAD_UNCHANGED)

    # template = cv2.imread(template_path, cv2.IMREAD_COLOR)
    if template is None:
        print(f"Template not found or invalid: {template_path}")
        return None
    
    if template.shape[2] == 4:
        template = cv2.cvtColor(template, cv2.COLOR_BGRA2BGR)

    screen_cv = cv2.cvtColor(np.array(screen_img), cv2.COLOR_RGB2BGR)

    # Check image compatibility
    if screen_cv.shape[0] < template.shape[0] or screen_cv.shape[1] < template.shape[1]:
        print(f"Template is larger than screenshot.")
        return None

    if screen_cv.dtype != template.dtype:
        print(f"Dtype mismatch: screen={screen_cv.dtype}, template={template.dtype}")
        return None

    result = cv2.matchTemplate(screen_cv, template, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(result)

    if max_val >= threshold:
        h, w = template.shape[:2]
        return (max_loc[0] + w // 2, max_loc[1] + h // 2)

    return None

def ExtractText(image: Image.Image) -> str:
    gray = image.convert('L')  # Convert to grayscale
    text = pytesseract.image_to_string(gray)
    return text.lower().strip()

def WaitForImage(image_path):
    """
    Waits until the specified image appears on the screen or timeout is reached.
    Returns (x, y) coordinates if found, else None.
    """
    start_time = time.time()
    while time.time() - start_time < WAIT_TIMEOUT:
        screen = GetScreenshot()
        coords = FindTemplate(screen, image_path)
        if coords:
            return coords
        time.sleep(WAIT_POLL)
    return None

def FindOnScreen(template_path, retries=1, delay=0):
    """
    Takes a screenshot and returns coordinates of the matched template image.
    """
    for i in range(retries):
        screen = GetScreenshot()
        coords = FindTemplate(screen, template_path)
        if coords:
            return coords
        if delay > 0:
            time.sleep(delay)
    return None

def CountMatches(screen_img, template_path, threshold=0.9):
    screen_cv = cv2.cvtColor(np.array(screen_img), cv2.COLOR_RGB2BGR)
    template = cv2.imread(template_path, cv2.IMREAD_COLOR)

    if template is None:
        print(f"Template not found: {template_path}")
        return 0

    result = cv2.matchTemplate(screen_cv, template, cv2.TM_CCOEFF_NORMED)
    match_locations = np.where(result >= threshold)
    count = len(list(zip(*match_locations[::-1])))
    return count

def FindAllTemplates(screen_img, templates: dict, threshold=0.85, use_gray=True):
    """
    Finds all instances of multiple template images in a screenshot.
    
    Args:
        screen_img (PIL.Image): The screenshot image.
        templates (dict): A dictionary with keys as labels and values as template image paths.
        threshold (float): Minimum matching threshold.
        use_gray (bool): If True, convert both images to grayscale to ignore color.
    
    Returns:
        List of dicts: [{ "type": <label>, "coords": (x, y) }, ...]
    """
    if screen_img is None:
        print("No screenshot provided.")
        return []

    matches = []
    screen_cv = cv2.cvtColor(np.array(screen_img), cv2.COLOR_RGB2GRAY if use_gray else cv2.COLOR_RGB2BGR)

    for label, template_path in templates.items():
        template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE if use_gray else cv2.IMREAD_COLOR)
        if template is None:
            print(f"Template not found or invalid: {template_path}")
            continue

        if screen_cv.shape[0] < template.shape[0] or screen_cv.shape[1] < template.shape[1]:
            print(f"Template too large for screen: {template_path}")
            continue

        result = cv2.matchTemplate(screen_cv, template, cv2.TM_CCOEFF_NORMED)
        locations = np.where(result >= threshold)

        for pt in zip(*locations[::-1]):
            w, h = template.shape[1], template.shape[0]
            center = (pt[0] + w // 2, pt[1] + h // 2)
            matches.append({ "type": label, "coords": center })

    return matches

def TapWithRetry(image, label, retries=3):
    fallback_keywords = ["tap anywhere to exit", "anywhere", "exit", "rewards", "victory"]
    for attempt in range(1, retries + 1):
        coords = FindOnScreen(image)
        if coords:
            print(f"{label} found on attempt {attempt}, tapping...")
            Tap(*coords)
            time.sleep(SLEEP_TIME)
            return True
        else:
            print(f"{label} not found (attempt {attempt}), retrying...")
            PressBack()
            time.sleep(SLEEP_TIME)
    print(f"Failed to find {label} after {retries} attempts.")
    return False

def ScreenHasText(keywords: list, screenshot=None) -> bool:
    if not screenshot:
        screenshot = GetScreenshot()

    text = ExtractText(screenshot)
    return any(word.lower() in text for word in keywords)


def DetectNewTasks(baseline_path, threshold=40, min_area=500, ignore_y_range=(860, 960)):

    baseline = cv2.imread(baseline_path, cv2.IMREAD_GRAYSCALE)
    current = GetScreenshotCV()  # This should return a current screenshot in OpenCV format
    current_gray = cv2.cvtColor(current, cv2.COLOR_BGR2GRAY)

    # Ensure same size
    if baseline.shape != current_gray.shape:
        current_gray = cv2.resize(current_gray, (baseline.shape[1], baseline.shape[0]))

    # Compute difference and threshold
    diff = cv2.absdiff(current_gray, baseline)
    _, thresh = cv2.threshold(diff, threshold, 255, cv2.THRESH_BINARY)

    # Morphological clean-up
    kernel = np.ones((5, 5), np.uint8)
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)

    # Find contours of changes
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Filter and extract task positions
    tasks = []
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area >= min_area:
            x, y, w, h = cv2.boundingRect(cnt)
            center_x = x + w // 2
            center_y = y + h // 2

            if ignore_y_range[0] <= center_y <= ignore_y_range[1]:
                continue  # Skip ignored region

            tasks.append((center_x, center_y))

    return tasks


def FindWithRetries(find_fn, label="element", attempts=3, delay=SLEEP_TIME):
    """
    Tries to locate something on screen with retries.

    Args:
        find_fn: A lambda or function returning coordinates or None.
        label (str): Text to display while retrying.
        attempts (int): Number of attempts before giving up.
        delay (float): Delay between attempts.

    Returns:
        Found value or None
    """
    for attempt in range(1, attempts + 1):
        result = find_fn()
        if result:
            print(f"{label} found on attempt {attempt}")
            return result
        print(f"{label} not found (attempt {attempt})")
        time.sleep(delay)
    print(f"{label} not found after {attempts} attempts.")
    return None

