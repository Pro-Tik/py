import requests

def load_proxy_urls(filename):
    """
    Load proxy URLs from a text file, where each line contains a URL.
    """
    with open(filename, 'r') as f:
        urls = [line.strip() for line in f if line.strip()]
    print(f"Loaded {len(urls)} URLs from {filename}")
    return urls

def download_proxies(urls):
    """
    Download proxies from the given URLs and store them in a list.
    """
    all_proxies = []
    for url in urls:
        print(f"Attempting to download from: {url}")
        try:
            response = requests.get(url)
            response.raise_for_status()  # Raise an error for bad responses
            proxies = response.text.splitlines()
            all_proxies.extend(proxies)
            print(f"Downloaded {len(proxies)} proxies from {url}.")
        except requests.RequestException as e:
            print(f"Failed to download from {url}: {e}")
    return all_proxies

def reformat_proxies(proxy_list, proxy_type="http"):
    """
    Reformat each proxy by adding the proxy type.
    Assumes each proxy is in the format 'ip:port:user:password'.
    """
    formatted_proxies = []
    for proxy in proxy_list:
        print(f"Raw proxy: {proxy}")  # Debug output to see the raw proxy format
        parts = proxy.split(":")
        if len(parts) == 4:  # 'IP:PORT:username:password' format expected
            ip_port = parts[0] + ":" + parts[1]
            username = parts[2]
            password = parts[3]
            formatted_proxy = f"{proxy_type}://{username}:{password}@{ip_port}"
            formatted_proxies.append(formatted_proxy)
            print(f"Formatted proxy: {formatted_proxy}")
        else:
            print(f"Warning: Proxy format is incorrect: {proxy}")
    return formatted_proxies

def save_proxies(formatted_proxies, filename):
    """
    Save formatted proxies to a text file, one per line.
    """
    with open(filename, 'w') as f:
        for proxy in formatted_proxies:
            f.write(f"{proxy}\n")
    print(f"Formatted proxies saved to {filename}")

def main():
    """
    Main function to load URLs, download proxies, format them, and save to a file.
    """
    proxy_urls = load_proxy_urls("auth.txt")  # Load proxy URLs from auth.txt
    
    all_proxies = download_proxies(proxy_urls)
    formatted_proxies = reformat_proxies(all_proxies, proxy_type="http")
    save_proxies(formatted_proxies, "proxies.txt")

# Ensure this block is correctly written to allow the script to run as the main program
if __name__ == "__main__":
    main()
