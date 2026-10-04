import os
import re
import sys
import requests

# 1. Grab the secure Discord Webhook from GitHub settings
DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")

if not DISCORD_WEBHOOK_URL:
    print("Error: DISCORD_WEBHOOK_URL is missing!")
    sys.exit(1)


def fetch_wardogs_gold_price():
    """Fetches the live gold price from the official WARDOGS site."""
    try:
        # We target the official Wardogs Gold Market page
        url = "https://wardogshub.gg"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        response = requests.get(url, headers=headers, timeout=15)

        if response.status_code != 200:
            return "Unknown (Site Error)"

        # Search the page HTML for the dollar price pattern (e.g., $166,000)
        matches = re.findall(r"\$\d{1,3}(?:,\d{3})*", response.text)

        if matches:
            # Return the first dollar value found on the market page
            return matches[0]

        return "Unknown (Price Not Found)"
    except Exception as e:
        print(f"Scraping error: {e}")
        return "Unknown (Error)"


def send_to_discord():
    price = fetch_wardogs_gold_price()

    # Structure a clean Discord Embed message
    payload = {
        "embeds": [
            {
                "title": "💰 WARDOGS Gold Market Update",
                "description": f"The current exchange rate for **1 Gold Bar** has been updated.",
                "color": 16761035,  # Gold Color Hex
                "fields": [
                    {
                        "name": "Current Price",
                        "value": f"**{price}** In-Game Cash",
                        "inline": False,
                    }
                ],
                "footer": {
                    "text": "Automated Daily Update • Click title to visit market",
                    "icon_url": "https://wardogshub.gg",
                },
                "url": "https://wardogshub.gg",
            }
        ]
    }

    # Send it to your Discord Channel
    response = requests.post(DISCORD_WEBHOOK_URL, json=payload)
    if response.status_code == 204:
        print("Success: Price posted to Discord!")
    else:
        print(f"Failed to send to Discord: {response.status_code}")


if __name__ == "__main__":
    send_to_discord()
