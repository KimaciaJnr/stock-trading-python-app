import time
from datetime import datetime

import schedule

from script import run_stock_job


def stock_job():
    print(f"Stock job started: {datetime.now()}")

    try:
        run_stock_job()
        print(f"Stock job completed: {datetime.now()}")

    except Exception as error:
        print(f"Stock job failed: {error}")


# Run the stock job every minute
schedule.every().minute.do(stock_job)


if __name__ == "__main__":
    while True:
        schedule.run_pending()
        time.sleep(1)