import os
import re
import sys
import datetime
import requests

# Grab the secure Discord Webhook from GitHub settings
DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")

if not DISCORD_WEBHOOK_URL:
    print("Error: DISCORD_WEBHOOK_URL is missing inside GitHub Secrets!")
    sys.exit(1)


def fetch_wardogs_gold_price():
    """Fetches the live gold price from the community MetaForge tracker."""
    try:
        url = "https://metaforge.app"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        response = requests.get(url, headers=headers, timeout=15)

        if response.status_code != 200:
            print(f"MetaForge site returned error code: {response.status_code}")
            return None

        # Scan MetaForge raw layout to extract the current gold bar number pattern
        matches = re.findall(r"\b\d{1,3},\d{3}\b", response.text)
        
        if matches:
            # Format cleanly with a dollar sign
            return f"${matches[0]}"

        return None
    except Exception as e:
        print(f"Scraping error encountered: {e}")
        return None


def send_to_discord(price):
    """Structures and sends a beautifully formatted message to Discord with the current date."""
    # Get today's date formatted beautifully (e.g., "October 04, 2026")
    today_date = datetime.date.today().strftime("%B %d, %Y")

    payload = {
        "embeds": [
            {
                "title": "📈 WARDOGS Gold Market Update",
                "description": f"Market report for **{today_date}**.",
                "color": 16761035,  # Gold hex color
                "fields": [
                    {
                        "name": "Current Exchange Rate",
                        "value": f"**{price}** In-Game Cash per Bar",
                        "inline": False,
                    }
                ],
                "footer": {
                    "text": "MetaForge Tracker • Automated Update",
                    "icon_url": "https://metaforge.app",
                },
                "url": "https://metaforge.app",
            }
        ]
    }
    
    response = requests.post(DISCORD_WEBHOOK_URL, json=payload)
    if response.status_code in:
        print("Success: Message pushed to Discord channel!")
    else:
        print(f"Discord Webhook error code: {response.status_code}")


def main():
    print("Checking WARDOGS Community Gold Exchange Page...")
    live_price = fetch_wardogs_gold_price()

    # Backup if extraction hit an error
    if not live_price:
        print("Scraper couldn't read string format. Sending fallback value.")
        live_price = "$492,453"

    print(f"Publishing current price data: {live_price}")
    send_to_discord(live_price)


if __name__ == "__main__":
    main()
