import csv
import os
import time

import requests
from dotenv import load_dotenv


class StockJob:
    BASE_URL = "https://api.massive.com/v3/reference/tickers"

    FIELDS = [
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

    def __init__(self):
        load_dotenv()

        self.api_key = os.getenv("POLYGON_API_KEY")

        if not self.api_key:
            raise RuntimeError("POLYGON_API_KEY is not set.")

        self.limit = 1000
        self.max_retries = 3
        self.retry_delay = 60
        self.output_file = "tickers.csv"

        self.session = requests.Session()

    def _request(self, url, params=None):
        for _ in range(self.max_retries):
            response = self.session.get(
                url,
                params=params,
                timeout=30,
            )

            data = response.json()

            if data.get("status") != "ERROR":
                return data

            error = data.get("error", "Unknown API error")

            if "maximum requests per minute" in error.lower():
                time.sleep(self.retry_delay)
                continue

            raise RuntimeError(f"API error: {error}")

        raise RuntimeError("Maximum retry attempts exceeded.")

    def fetch_tickers(self):
        params = {
            "market": "stocks",
            "active": "true",
            "order": "asc",
            "limit": self.limit,
            "sort": "ticker",
            "apiKey": self.api_key,
        }

        tickers = []
        url = self.BASE_URL

        while url:
            data = self._request(
                url,
                params=params if url == self.BASE_URL else None,
            )

            tickers.extend(data.get("results", []))

            url = data.get("next_url")

            if url:
                url = f"{url}&apiKey={self.api_key}"

            time.sleep(1)

        return tickers

    def save_to_csv(self, tickers):
        with open(
            self.output_file,
            "w",
            newline="",
            encoding="utf-8",
        ) as file:
            writer = csv.DictWriter(
                file,
                fieldnames=self.FIELDS,
                extrasaction="ignore",
            )

            writer.writeheader()
            writer.writerows(tickers)

    def run(self):
        tickers = self.fetch_tickers()
        self.save_to_csv(tickers)

        return len(tickers)


def run_stock_job():
    """Run the stock extraction job."""
    return StockJob().run()


if __name__ == "__main__":
    run_stock_job()