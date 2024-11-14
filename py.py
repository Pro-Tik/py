import subprocess
import json
import time
import requests

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

def get_notifications():
    try:
        # Capture notifications using termux-notification-list
        notifications_raw = subprocess.check_output("termux-notification-list", shell=True, stderr=subprocess.PIPE)
        notifications = json.loads(notifications_raw.decode('utf-8'))
        return notifications
    except Exception as e:
        print(f"Error fetching notifications: {e}")
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
        time.sleep(10)  # Wait for 10 seconds before checking again

if __name__ == "__main__":
    main()
