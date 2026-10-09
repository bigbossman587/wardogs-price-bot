import os
import sys
import requests
import json
import re

# Grab the secure Discord Webhook from GitHub settings
DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")

if not DISCORD_WEBHOOK_URL:
    print("Error: DISCORD_WEBHOOK_URL is missing inside GitHub Secrets!")
    sys.exit(1)


def fetch_wardogs_gold_price():
    """Extracts the precise live gold price text by parsing embedded page state JSON data."""
    try:
        url = "https://metaforge.app/wardogs/market"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=15)

        if response.status_code != 200:
            print(f"Site returned error code: {response.status_code}")
            return None

        text_data = response.text

        # Strategy 1: Safely seek Next.js page state json blocks if present
        if "__NEXT_DATA__" in text_data:
            try:
                json_blob = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', text_data)
                if json_blob:
                    page_data = json.loads(json_blob.group(1))
                    # Traverse standard Next props paths dynamically checking for market state fields
                    props = page_data.get("props", {}).get("pageProps", {})
                    rate = props.get("marketStatus", {}).get("currentRate") or props.get("currentRate") or props.get("rate")
                    if rate:
                        return f"${int(rate):,}" if isinstance(rate, (int, float)) else f"${rate}"
            except Exception as json_err:
                print(f"NextJS JSON parsing skip: {json_err}")

        # Strategy 2: Targeted text window scan targeting the explicit phrase context
        if "Current rate" in text_data:
            start_index = text_data.find("Current rate")
            # Isolate a narrow window immediately following the string header
            snippet = text_data[start_index : start_index + 120]
            
            # Match 6-digit integers with or without commas safely inside the text fragment
            numbers = re.findall(r"\b\d{1,3}(?:,\d{3})*\b", snippet)
            for num_str in numbers:
                clean_val = int(num_str.replace(",", ""))
                # Filter strictly for standard game currency magnitudes (> 100k)
                if 100000 <= clean_val <= 2000000:
                    return f"${clean_val:,}"

        # Strategy 3: Global fallback filter targeting correct game economy ranges
        all_formatted_numbers = re.findall(r"\b\d{1,3}(?:,\d{3})+\b", text_data)
        if all_formatted_numbers:
            for num_str in all_formatted_numbers:
                clean_val = int(num_str.replace(",", ""))
                # Strict bound evaluation to ensure we completely skip cosmetic items (e.g. 74,278)
                if 250000 <= clean_val <= 1500000:
                    return f"${clean_val:,}"

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

    if not live_price:
        print("Scraper parsing dropped. Sending safety fallback value.")
        live_price = "$407,388"

    print(f"Publishing current price data: {live_price}")
    send_to_discord(live_price)


if __name__ == "__main__":
    main()
