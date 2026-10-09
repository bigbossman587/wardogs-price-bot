import os
import sys
import requests
import re

# Grab the secure Discord Webhook from GitHub settings
DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")

if not DISCORD_WEBHOOK_URL:
    print("Error: DISCORD_WEBHOOK_URL is missing inside GitHub Secrets!")
    sys.exit(1)


def fetch_wardogs_gold_price():
    """Extracts the floating live gold market price text cleanly from the source."""
    try:
        url = "https://metaforge.app/wardogs/market"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
        }
        response = requests.get(url, headers=headers, timeout=15)

        if response.status_code != 200:
            print(f"Site returned error code: {response.status_code}")
            return None

        text_data = response.text
        
        # 1. Search for the pattern explicitly mentioned on the page text
        if "Current rate" in text_data:
            start_index = text_data.find("Current rate")
            # Pull a target window around the rate to isolate the number
            snippet = text_data[start_index : start_index + 60]
            
            # Match number formatted with commas (e.g., 459,112)
            numbers = re.findall(r"\d{1,3}(?:,\d{3})+", snippet)
            if numbers:
                return f"${numbers[0]}"
                
        # 2. Resilient backup regex: Scan the entire document if the text layout slightly shifts
        all_formatted_numbers = re.findall(r"\b\d{1,3}(?:,\d{3})+\b", text_data)
        if all_formatted_numbers:
            # The first large comma-separated sequence on this specific page is consistently the exchange rate
            for num_str in all_formatted_numbers:
                # Filter out values that are too small to be the market exchange price
                clean_val = int(num_str.replace(",", ""))
                if clean_val > 50000:
                    return f"${num_str}"

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
                },
                "url": "https://metaforge.app/wardogs/market",
            }
        ]
    }
    
    response = requests.post(DISCORD_WEBHOOK_URL, json=payload)
    
    if response.status_code == 200 or response.status_code == 204:
        print("Success: Message pushed to Discord channel!")
    else:
        print(f"Discord Webhook error code: {response.status_code}")


def main():
    print("Checking WARDOGS Gold Exchange Page...")
    live_price = fetch_wardogs_gold_price()

    # Safety fall-through tracking tag to see if it used a live pull or the static baseline
    if not live_price:
        print("Scraper parsing dropped. Sending fallback baseline.")
        live_price = "$326,749 (Fallback Value)"

    print(f"Publishing current price data: {live_price}")
    send_to_discord(live_price)


if __name__ == "__main__":
    main()
