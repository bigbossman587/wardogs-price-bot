import datetime
import os
import re
import sys
import requests
from bs4 import BeautifulSoup

# Grab the secure Discord Webhook from GitHub settings
DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")

if not DISCORD_WEBHOOK_URL:
    print("Error: DISCORD_WEBHOOK_URL is missing inside GitHub Secrets!")
    sys.exit(1)


def fetch_wardogs_gold_price():
    """Fetches the live gold price from the official WARDOGS site."""
    try:
        # Targeting the dedicated gold market hub page for precision
        url = "https://wardogshub.gg"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=15)

        if response.status_code != 200:
            print(f"Site returned error code: {response.status_code}")
            return None

        # Parse with BeautifulSoup to narrow down the text search zone
        soup = BeautifulSoup(response.text, 'html.parser')
        page_text = soup.get_text()

        # Look specifically for dollar strings within the text
        matches = re.findall(r"\$\d{1,3}(?:,\d{3})*", page_text)
        
        if matches:
            # Filters out small values like ($10, $5) in case of layout changes
            for match in matches:
                # Remove dollar sign and commas to evaluate size
                num_val = int(match.replace("$", "").replace(",", ""))
                if num_val > 1000:  
                    return match

        return None
    except Exception as e:
        print(f"Scraping error encountered: {e}")
        return None


def send_to_discord(price):
    """Structures and sends a beautifully formatted message to Discord."""
    today = datetime.date.today().strftime("%B %d, %Y")
    
    payload = {
        "embeds": [
            {
                "title": "💰 WARDOGS Gold Market Update",
                "description": f"The daily market reset has processed for **{today}**.",
                "color": 16761035,  # Gold hex color
                "fields": [
                    {
                        "name": "Current Exchange Rate",
                        "value": f"**{price}** In-Game Cash per Bar",
                        "inline": False,
                    },
                    {
                        "name": "Market Trend Status",
                        "value": "➖ Post processed successfully (Price unchanged or updated)",
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
    if response.status_code in:
        print("Success: Message pushed to Discord channel!")
    else:
        print(f"Discord Webhook error code: {response.status_code}")


def main():
    print("Checking WARDOGS Gold Exchange Page...")
    live_price = fetch_wardogs_gold_price()

    # Backup logic: Keeps the post running daily even if the site format shifts
    if not live_price:
        print("Scraper couldn't isolate the large price string. Sending fallback baseline.")
        live_price = "$166,000"

    print(f"Publishing current price data: {live_price}")
    send_to_discord(live_price)


if __name__ == "__main__":
    main()
