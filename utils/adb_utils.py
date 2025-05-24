import subprocess

from config import DEVICE_ID, PACKAGE_NAME


def OpenApp():
    subprocess.run(['adb', '-s', DEVICE_ID, 'shell', 'monkey', '-p', PACKAGE_NAME, '-c', 'android.intent.category.LAUNCHER', '1'])

def Tap(x, y):
    subprocess.run(['adb', '-s', DEVICE_ID, 'shell', 'input', 'tap', str(x), str(y)])

def Swipe(x1, y1, x2, y2, duration=500):
    subprocess.run(['adb', '-s', DEVICE_ID, 'shell', 'input', 'swipe', str(x1), str(y1), str(x2), str(y2), str(duration)])

def PressBack():
    subprocess.run(['adb', '-s', DEVICE_ID, 'shell', 'input', 'keyevent', '4'])
