from fetcher import DataFetcher
import schedule
import time


class Scheduler:
    def __init__(self):
        self.schedule_per_type = {}
        self.fetcher = DataFetcher()

    def register(self, currency_type, interval_sec):
        self.schedule_per_type[currency_type] = interval_sec
        schedule.every(interval_sec).seconds.do(
            self.fetcher.fetch_price, currency_type)

    def start(self):
        while True:
            schedule.run_pending()
            time.sleep(1)
