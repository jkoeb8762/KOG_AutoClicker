import pyautogui
from PIL import ImageGrab
import json
import time
import os
import re
import pyscreeze

confidence = 0.8

def get_pixel_color(x, y):
    """Get the color of the pixel at the specified coordinates."""
    screen = ImageGrab.grab()
    return screen.getpixel((x, y))

# def click_pixel(image):
#     """Find and click the center of an image on the screen."""
#     try:
#         buttonx, buttony = pyautogui.locateCenterOnScreen(image, confidence=0.9)
#         pyautogui.click(buttonx, buttony)
#         return True
#     except pyautogui.ImageNotFoundException:
#         print(f'ImageNotFoundException: {image} not found')
#         return False

# def locate_and_move(image):
#     """Find and move to the center of an image on the screen."""
#     x, y = pyautogui.locateCenterOnScreen(image, confidence=0.9)
#     if x is None:
#         raise ValueError(f"{image} not found on screen")
#     pyautogui.moveTo(x, y)
#     return x, y

def click_pixel(image):
    """Find and click the center of an image on the screen with global confidence level."""
    global confidence
    try:
        buttonx, buttony = locate_center_on_screen(image)
        pyautogui.click(buttonx, buttony)
        return True
    except pyautogui.ImageNotFoundException as e:
        highest_confidence = get_highest_confidence_from_exception(str(e))
        print(f'ImageNotFoundException: {image} not found at confidence level {confidence}. Highest confidence detected: {highest_confidence}')
        return False

def locate_and_move(image):
    """Find and move to the center of an image on the screen with global confidence level."""
    global confidence
    try:
        x, y = locate_center_on_screen(image)
        pyautogui.moveTo(x, y)
        return x, y
    except pyautogui.ImageNotFoundException as e:
        highest_confidence = get_highest_confidence_from_exception(str(e))
        print(f"ImageNotFoundException: {image} not found at confidence level {confidence}. Highest confidence detected: {highest_confidence}")
        return None

def locate_center_on_screen(image):
    """Wrapper function to handle image location and extract confidence from exception."""
    global confidence
    try:
        return pyautogui.locateCenterOnScreen(image, confidence=confidence)
    except pyautogui.ImageNotFoundException:
        return None

def get_highest_confidence_from_exception(exception_message):
    """Extract the highest confidence level from the exception message."""
    match = re.search(r'highest confidence = ([\d.]+)', exception_message)
    return float(match.group(1)) if match else None

def load_config():
    if os.path.exists('config.json'):
        with open('config.json', 'r') as f:
            return json.load(f)
    return None

def save_config(data):
    with open('config.json', 'w') as f:
        json.dump(data, f, indent=4)
    
def setup():
    # Prompt user for target type
    print("手動自己點幾次 先把各種提示關閉")
    checker = input("增加到想要的屬性後停止 先不要選擇保留或使用原值 輸入y進入下一步").strip().lower()
    while(True):
        if checker == "y":
            target_type = input("輸入目標屬性 (str, int, or dex): ").strip().lower()
            break
        else:
            checker = input("輸入y進入下一步").strip().lower()

    if target_type not in {'str', 'int', 'dex'}:
        print("非法選項. 退出中.")
        return
    print("警告: 每次育成耗時約3秒。程式運行期間會無法使用電腦。")
    print("若中途要終止需與腳本爭奪鼠標控制權")
    print("少迴優化不佳長期運行 模擬器容易卡頓崩潰 建議輸入1000以下的數字")
    print("注意: 育成時 編隊只放一雜魚最好 越多腳色越容易卡頓")
    target_cycles = int(input("輸入育成次數: ").strip())
    target_image = f'resources/{target_type}.png'
    success_image = 'resources/success.png'

    #try:
    # Locate the center of the target image
    target_x, target_y = locate_and_move(target_image)
    if target_x is None or target_y is None:
        return None
    # Locate the center of the fail image
    resultarrow_x, resultarrow_y = locate_and_move(success_image)

    # Move to the fail image and get pixel color
    pyautogui.moveTo(resultarrow_x, target_y)
    color = get_pixel_color(resultarrow_x, target_y)

    # Store results
    result_data = {
        'target_cycles': target_cycles,
        'target_location': {'x': int(target_x), 'y': int(target_y)},  # Convert to native types
        'resultarrow_location': {'x': int(resultarrow_x), 'y': int(target_y)},  # Ensure integer values
        'result_color': list(color)  # Convert color tuple to list
    }
    return result_data

def auto_click():
    config = load_config()
    if config and input("使用上次的設定? (y/n): ").strip().lower() == 'y':
        data = config
    else:
        data = setup()
        if data:
            save_config(data)

    if not data:
        return
    print("選擇保留")
    input("確認育成按鈕可見後輸入任何按鍵: ")
    try:
        for i in range(int(data['target_cycles'])):
            time.sleep(1)
            if not click_pixel('resources/10x.png'):
                continue

            x, y = data['resultarrow_location']['x'], data['resultarrow_location']['y']
            color = data['result_color']
            time.sleep(1)
            while locate_center_on_screen('resources/keep_current.png') is None:
                time.sleep(1)
            if pyautogui.pixelMatchesColor(x, y, tuple(color)):
                click_pixel('resources/keep_current.png')
            else:
                click_pixel('resources/keep_former.PNG')
    except Exception as e:
        print(f"Unhandled exception: {str(e)}")

def display_terms_of_use():
    # Read and display the terms of use from a file
    with open('resources/TermsOfUse.txt', 'r', encoding='utf-8') as file:
        terms = file.read()
    print(terms)

def check_user_agreement():
    # Check if the user has already accepted the terms
    if not os.path.exists('user_agreement_accepted.txt'):
        display_terms_of_use()
        # Ask the user to accept the terms
        consent = input("您是否接受使用條款？(y/n): ").strip().lower()
        if consent == 'y':
            # Write to a file to record the acceptance
            with open('user_agreement_accepted.txt', 'w') as file:
                file.write("Accepted")
            return True
        else:
            print("您必須接受使用條款才能繼續使用此應用程序。")
            return False
    return True


def main():
    if check_user_agreement():
        print("正在進入應用程序...")
        auto_click()
    else:
        print("退出應用程序。")
    input("跑完啦~ 輸入任意按鈕即可退出")

if __name__ == '__main__':
    main()