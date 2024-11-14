import asyncio
import aiohttp
import time
import uuid
import cloudscraper
from loguru import logger
import sys
import json
import re
import subprocess

# Notification sender script (part of your original code)
async def send_notification(message):
    process = await asyncio.create_subprocess_exec(
        "termux-toast", message,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    if process.returncode == 0:
        print(f"Notification sent successfully: {message}")
    else:
        print(f"Error sending notification: {stderr.decode()}")

# Second script (your provided script)
def show_intro():
    banner = """
    
  ████████╗███████╗ █████╗ ███╗   ███╗    ██╗  ██╗██╗   ██╗███╗   ██╗████████╗███████╗██████╗ ███████╗
  ╚══██╔══╝██╔════╝██╔══██╗████╗ ████║    ██║  ██║██║   ██║████╗  ██║╚══██╔══╝██╔════╝██╔══██╗██╔════╝
     ██║   █████╗  ███████║██╔████╔██║    ███████║██║   ██║██╔██╗ ██║   ██║   █████╗  ██████╔╝█████╗  
     ██║   ██╔══╝  ██╔══██║██║╚██╔╝██║    ██╔══██║██║   ██║██║╚██╗██║   ██║   ██╔══╝  ██╔══██╗██╔══╝  
     ██║   ███████╗██║  ██║██║ ╚═╝ ██║    ██║  ██║╚██████╔╝██║ ╚████║   ██║   ███████╗██║  ██║███████╗
     ╚═╝   ╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝    ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝   ╚═╝   ╚══════╝╚═╝  ╚═╝╚══════╝

---------------------------------------------------------------------------------------------------------
    THIS IS A BYPASSED VERSION - BY TEAM HUNTERS (https://t.me/team_hunters0)                             
---------------------------------------------------------------------------------------------------------
"""
    for line in banner.splitlines():
        print(line)
        time.sleep(0.05)

def show_warning():
    show_intro()
    print("\nProceeding automatically...")

# Constants
PING_INTERVAL = 60
RETRIES = 60

DOMAIN_API = {
    "SESSION": "https://api.nodepay.ai/api/auth/session",
    "PING": "http://13.215.134.222/api/network/ping"
}

CONNECTION_STATES = {
    "CONNECTED": 1,
    "DISCONNECTED": 2,
    "NONE_CONNECTION": 3
}

status_connect = CONNECTION_STATES["NONE_CONNECTION"]
browser_id = None
account_info = {}
last_ping_time = {}

def uuidv4():
    return str(uuid.uuid4())

def valid_resp(resp):
    if not resp or "code" not in resp or resp["code"] < 0:
        raise ValueError("Invalid response")
    return resp

async def render_profile_info(proxy, token):
    global browser_id, account_info

    try:
        # Load session or initiate a new one
        np_session_info = load_session_info(proxy)
        if not np_session_info:
            browser_id = uuidv4()
            response = await call_api(DOMAIN_API["SESSION"], {}, proxy, token)
            valid_resp(response)
            account_info = response["data"]
            if account_info.get("uid"):
                save_session_info(proxy, account_info)
                await start_ping(proxy, token)
            else:
                handle_logout(proxy)
        else:
            account_info = np_session_info
            await start_ping(proxy, token)
    except Exception as e:
        logger.error(f"Error in render_profile_info for proxy {proxy}: {e}")
        if "keepalive ping timeout" in str(e) or "500 Internal Server Error" in str(e):
            logger.info(f"Removing proxy due to persistent error: {proxy}")
            remove_proxy_from_list(proxy)
        return

async def call_api(url, data, proxy, token):
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept": "application/json",
    }

    try:
        scraper = cloudscraper.create_scraper()
        response = scraper.post(url, json=data, headers=headers, proxies={ 
                                "http": proxy, "https": proxy}, timeout=30)
        response.raise_for_status()
        return valid_resp(response.json())
    except Exception as e:
        logger.error(f"Error during API call to {url}: {e}")
        raise ValueError(f"Failed API call to {url}")

async def start_ping(proxy, token):
    try:
        while True:
            await ping(proxy, token)
            await asyncio.sleep(PING_INTERVAL)
    except asyncio.CancelledError:
        logger.info(f"Ping task cancelled for proxy {proxy}")
    except Exception as e:
        logger.error(f"Error in ping task for proxy {proxy}: {e}")
        
async def ping(proxy, token):
    global last_ping_time, RETRIES, status_connect

    current_time = time.time()
    if proxy in last_ping_time and (current_time - last_ping_time[proxy]) < PING_INTERVAL:
        logger.info(f"Skipping ping for proxy {proxy}, not enough time elapsed")
        return

    last_ping_time[proxy] = current_time

    try:
        data = {
            "id": account_info.get("uid"),
            "browser_id": browser_id,
            "timestamp": int(time.time())
        }

        response = await call_api(DOMAIN_API["PING"], data, proxy, token)
        if response["code"] == 0:
            logger.info(f"Ping successful for proxy {proxy}: {response}")
            RETRIES = 0
            status_connect = CONNECTION_STATES["CONNECTED"]
        else:
            handle_ping_fail(proxy, response)
    except Exception as e:
        logger.error(f"Ping failed for proxy {proxy}: {e}")
        handle_ping_fail(proxy, None)

def handle_ping_fail(proxy, response):
    global RETRIES, status_connect

    RETRIES += 1
    if response and response.get("code") == 403:
        handle_logout(proxy)
    elif RETRIES < 2:
        status_connect = CONNECTION_STATES["DISCONNECTED"]
    else:
        status_connect = CONNECTION_STATES["NONE_CONNECTION"]

def handle_logout(proxy):
    global status_connect, account_info
    status_connect = CONNECTION_STATES["NONE_CONNECTION"]
    account_info = {}
    logger.info(f"Logged out for proxy {proxy}")

def sanitize_proxy_url(proxy_url):
    # Replace characters like : and / with _
    return re.sub(r'[^a-zA-Z0-9]', '_', proxy_url)

def load_session_info(proxy):
    sanitized_proxy = sanitize_proxy_url(proxy)
    try:
        # Load session info from a file or database for the proxy
        with open(f"session_{sanitized_proxy}.json", 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.info(f"No session file found for proxy {proxy}, creating new session.")
        return None
    except Exception as e:
        logger.error(f"Error loading session info for proxy {proxy}: {e}")
        return None

def save_session_info(proxy, account_info):
    sanitized_proxy = sanitize_proxy_url(proxy)
    try:
        # Save session info to a file or database for the proxy
        with open(f"session_{sanitized_proxy}.json", 'w') as f:
            json.dump(account_info, f)
    except Exception as e:
        logger.error(f"Error saving session info for proxy {proxy}: {e}")

def load_proxies(file):
    try:
        with open(file, 'r') as f:
            return [line.strip() for line in f if line.strip()]
    except Exception as e:
        logger.error(f"Failed to load proxies from {file}: {e}")
        sys.exit(1)

def load_tokens(file):
    try:
        with open(file, 'r') as f:
            return [line.strip() for line in f if line.strip()]
    except Exception as e:
        logger.error(f"Failed to load tokens from {file}: {e}")
        sys.exit(1)

def assign_proxies_to_tokens(proxies, tokens, group_size=10):
    mapping = {}
    for i, token in enumerate(tokens):
        start = i * group_size
        end = start + group_size
        mapping[token] = proxies[start:end]
    return mapping

async def run_account(token, proxies):
    tasks = [render_profile_info(proxy, token) for proxy in proxies]
    await asyncio.gather(*tasks)

async def run_scripts():
    proxies = load_proxies('proxies.txt')
    tokens = load_tokens('token.txt')

    mapping = assign_proxies_to_tokens(proxies, tokens)

    for token, proxies_for_token in mapping.items():
        await run_account(token, proxies_for_token)

# Main entry point to execute both scripts
async def main():
    try:
        await asyncio.gather(
            run_scripts(),
            send_notification("Both scripts are running concurrently!")
        )
    except Exception as e:
        logger.error(f"Error in main task: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
