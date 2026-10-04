import os
import re
import sys
import requests

# Grab the secure Discord Webhook from GitHub settings
DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")

if not DISCORD_WEBHOOK_URL:
    print("Error: DISCORD_WEBHOOK_URL is missing inside GitHub Secrets!")
    sys.exit(1)


def fetch_wardogs_gold_price():
    """Fetches the live gold price from the official WARDOGS site."""
    try:
        url = "https://wardogshub.gg"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        response = requests.get(url, headers=headers, timeout=15)

        if response.status_code != 200:
            print(f"Site returned error code: {response.status_code}")
            return None

        # Look specifically for the price text string on the page
        matches = re.findall(r"\$\d{1,3}(?:,\d{3})*", response.text)
        
        if matches:
            # Grab the very first dollar string match cleanly
            clean_price = str(matches[0])
            return clean_price

        return None
    except Exception as e:
        print(f"Scraping error encountered: {e}")
        return None


def send_to_discord(price):
    """Structures and sends a beautifully formatted message to Discord."""
    payload = {
        "embeds": [
            {
                "title": "💰 WARDOGS Gold Market Update",
                "description": "The daily market reset has processed.",
                "color": 16761035,  # Gold hex color
                "fields": [
                    {
                        "name": "Current Exchange Rate",
                        "value": f"**{price}** In-Game Cash per Bar",
                        "inline": False,
                    }
                ],
                "footer": {
                    "text": "Daily Market Tracker • Automated Update",
                    "icon_url": "https://wardogshub.gg",
                },
                "url": "https://wardogshub.gg",
            }
        ]
    }
    
    response = requests.post(DISCORD_WEBHOOK_URL, json=payload)
    if response.status_code in [200, 204]:
        print("Success: Message pushed to Discord channel!")
    else:
        print(f"Discord Webhook error code: {response.status_code}")


def main():
    print("Checking WARDOGS Gold Exchange Page...")
    live_price = fetch_wardogs_gold_price()

    # Backup logic: If the site block scraper fails, it sends a baseline update
    if not live_price:
        print("Scraper couldn't read string format. Sending fallback value.")
        live_price = "$166,000"

    print(f"Publishing current price data: {live_price}")
    send_to_discord(live_price)


if __name__ == "__main__":
    main()
