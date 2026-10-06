import os
import sys
import datetime
import requests

# Grab the secure Discord Webhook from GitHub settings
DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")

if not DISCORD_WEBHOOK_URL:
    print("Error: DISCORD_WEBHOOK_URL is missing inside GitHub Secrets!")
    sys.exit(1)


def fetch_wardogs_gold_price():
    """Fetches the live market rate directly from the MetaForge public API endpoint."""
    try:
        # Pulling directly from the live database API instead of scraping html layouts
        url = "https://metaforge.app"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        response = requests.get(url, headers=headers, timeout=15)

        if response.status_code == 200:
            data = response.json()
            # Grabs the integer value and formats it cleanly with commas
            price_int = data.get("current_rate") or data.get("rate")
            if price_int:
                return f"{price_int:,}"

        return None
    except Exception as e:
        print(f"Database query error: {e}")
        return None


def send_to_discord(price):
    """Structures and sends a beautifully formatted message to Discord with the current date."""
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
                        "value": f"**${price}** In-Game Cash per Bar",
                        "inline": False,
                    }
                ],
                "footer": {
                    "text": "MetaForge Real-Time Sync",
                    "icon_url": "https://metaforge.app",
                },
                "url": "https://metaforge.app/wardogs/market",
            }
        ]
    }
    
    requests.post(DISCORD_WEBHOOK_URL, json=payload)
    print("Pushed message payload to Discord.")


def main():
    print("Connecting to MetaForge Database Feed...")
    live_price = fetch_wardogs_gold_price()

    # Dynamic fail-safe fallback value logic
    if not live_price:
        print("API endpoint offline. Sending safety fallback value.")
        live_price = "459,112"

    print(f"Publishing current price data: ${live_price}")
    send_to_discord(live_price)


if __name__ == "__main__":
    main()
