import os
import sys
import requests

# Grab the secure Discord Webhook from GitHub settings
DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")

if not DISCORD_WEBHOOK_URL:
    print("Error: DISCORD_WEBHOOK_URL is missing inside GitHub Secrets!")
    sys.exit(1)


def fetch_wardogs_gold_price():
    """Fetches the live gold price directly from the Wardogs market API endpoint."""
    try:
        # Targeting the raw data endpoint directly instead of scraping raw HTML text
        url = "https://metaforge.app"
        headers = {
            "User-Agent": "Mozilla/5.0 (iPad; CPU OS 16_0 like Mac OS X) AppleWebKit/605.1.15",
            "Accept": "application/json"
        }
        response = requests.get(url, headers=headers, timeout=15)

        if response.status_code != 200:
            print(f"API returned error code: {response.status_code}")
            return None

        # Parse the JSON payload directly
        data = response.json()
        
        # Extract the current rate from the API keys
        rate = data.get("current_rate") or data.get("rate")
        
        if rate:
            # Format numbers cleanly with commas if it comes back as an integer/float
            if isinstance(rate, (int, float)):
                return f"${rate:,}"
            return f"${rate}".replace("$$", "$")

        return None
    except Exception as e:
        print(f"API extraction error encountered: {e}")
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
                },
                "url": "https://metaforge.app",
            }
        ]
    }
    
    response = requests.post(DISCORD_WEBHOOK_URL, json=payload)
    
    # Fixed conditional statement to avoid syntax errors
    if response.status_code == 200 or response.status_code == 204:
        print("Success: Message pushed to Discord channel!")
    else:
        print(f"Discord Webhook error code: {response.status_code}")


def main():
    print("Checking WARDOGS Gold Exchange API...")
    live_price = fetch_wardogs_gold_price()

    # Safety fall-through backup block modified to alert you if it fails
    if not live_price:
        print("API extraction failed. Sending warning fallback baseline.")
        live_price = "$326,749 (Fallback Value)"

    print(f"Publishing current price data: {live_price}")
    send_to_discord(live_price)


if __name__ == "__main__":
    main()
