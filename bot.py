import os
import re
import sys
import requests

# Grab secure Discord Webhook and GitHub passes
DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
REPOSITORY = os.environ.get("GITHUB_REPOSITORY")

if not DISCORD_WEBHOOK_URL:
    print("Error: DISCORD_WEBHOOK_URL is missing!")
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
            return None

        # Search the page HTML for the dollar price pattern (e.g., $166,000)
        matches = re.findall(r"\$\d{1,3}(?:,\d{3})*", response.text)
        if matches:
            return str(matches[0])  # Extracts the exact first clean price string found

        return None
    except Exception as e:
        print(f"Scraping error: {e}")
        return None


def get_last_saved_price():
    """Reads the price we saved yesterday from our log file."""
    if os.path.exists("last_price.txt"):
        with open("last_price.txt", "r") as f:
            return f.read().strip()
    return ""


def save_new_price(price):
    """Saves the new price locally so we can compare it tomorrow."""
    with open("last_price.txt", "w") as f:
        f.write(price)


def send_to_discord(price):
    """Structures and sends a beautifully formatted message to Discord."""
    payload = {
        "embeds": [
            {
                "title": "⚖️ WARDOGS Gold Price Shifted!",
                "description": "The daily market reset just went through with a price change.",
                "color": 16761035,  # Gold hex code
                "fields": [
                    {
                        "name": "New Exchange Rate",
                        "value": f"**{price}** In-Game Cash per Bar",
                        "inline": False,
                    }
                ],
                "footer": {
                    "text": "Market Shift Alert • Price tracked automatically",
                    "icon_url": "https://wardogshub.gg",
                },
                "url": "https://wardogshub.gg",
            }
        ]
    }
    requests.post(DISCORD_WEBHOOK_URL, json=payload)


def main():
    live_price = fetch_wardogs_gold_price()

    if not live_price:
        print("Could not fetch the live price right now. Aborting.")
        return

    last_price = get_last_saved_price()

    print(f"Live Price: {live_price} | Last Recorded Price: {last_price}")

    if live_price == last_price:
        print("Price hasn't changed since the last check. No Discord message sent.")
    else:
        print("Price change detected! Alerting Discord...")
        send_to_discord(live_price)
        save_new_price(live_price)


if __name__ == "__main__":
    main()
