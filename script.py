import os
import time
import csv
import requests
from dotenv import load_dotenv

load_dotenv()

# Load API configuration
API_KEY = os.getenv("POLYGON_API_KEY")
BASE_URL = "https://api.massive.com/v3/reference/tickers"
LIMIT = 1000
MAX_RETRIES = 3
RETRY_DELAY = 60
OUTPUT_FILE = "tickers.csv"

if not API_KEY:
    raise RuntimeError("POLYGON_API_KEY is not set.")


def fetch_tickers():
    params = {
        "market": "stocks",
        "active": "true",
        "order": "asc",
        "limit": LIMIT,
        "sort": "ticker",
        "apiKey": API_KEY,
    }

    tickers = []
    url = BASE_URL

    while url:

        # Retry failed requests
        for attempt in range(MAX_RETRIES):
            response = requests.get(
                url,
                params=params if url == BASE_URL else None,
                timeout=30,
            )

            data = response.json()

            if data.get("status") != "ERROR":
                break

            error = data.get("error", "Unknown API error")

            if "maximum requests per minute" in error.lower():
                time.sleep(RETRY_DELAY)
                continue

            raise RuntimeError(f"API error: {error}")

        else:
            raise RuntimeError("Maximum retry attempts exceeded.")

        # Add current page results
        tickers.extend(data.get("results", []))

        # Get next page
        url = data.get("next_url")

        if url:
            url = f"{url}&apiKey={API_KEY}"

        time.sleep(1)

    return tickers


def save_to_csv(tickers):
    fields = [
        "ticker",
        "name",
        "market",
        "locale",
        "primary_exchange",
        "type",
        "active",
        "currency_name",
        "cik",
        "composite_figi",
        "share_class_figi",
        "last_updated_utc",
    ]

    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=fields,
            extrasaction="ignore",
        )

        writer.writeheader()
        writer.writerows(tickers)


if __name__ == "__main__":
    tickers = fetch_tickers()
    save_to_csv(tickers)

    print(f"Extracted {len(tickers)} tickers.")
    print(f"Saved to {OUTPUT_FILE}")