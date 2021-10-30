import csv
import datetime
import os
import requests
import time
from time_converter import epoch_to_date_hour
"""
Simple fetcher to get the current price of a given type
"""


class DataFetcher:
    PRICE_API = 'https://api.cryptowat.ch/markets/kraken/{}/price'

    def fetch_price(self, currency_type):
        try:
            response = requests.get(self.PRICE_API.format(currency_type))
            fetch_time = int(time.time())
        except requests.exceptions.RequestException as e:
            # TODO: add retry logic
            print(
                'Cannot fetch response from cryptowat API. Exception: {}'.format(e.__str__))
            return

        if not self._validate_response(response):
            print('Reponse does not have the right format to process {}'.format(response))
            return

        current_price = {
            'price': response.json().get('result').get('price'),
            'type': currency_type,
            'timestamp': fetch_time,
        }
        print('Fetched price: ' + str(current_price))
        self._persist(current_price)
        return current_price

    def _persist(self, price):
        hour_file_name = epoch_to_date_hour(price['timestamp'])
        dir = 'data/{}'.format(price['type'])
        filepath = '{}/{}.csv'.format(dir, hour_file_name)
        self._ensure_path(dir)
        fieldnames = ['timestamp', 'price']
        price.pop('type', None)
        with open(filepath, mode='a+') as file:
            file_writer = csv.DictWriter(file, fieldnames=fieldnames)
            file_writer.writerow(price)

    def _ensure_path(self, filepath):
        isExist = os.path.exists(filepath)
        if not isExist:
            os.makedirs(filepath)

    def _validate_response(self, response):
        if response and response.json() != "":
            if 'result' in response.json() and 'price' in response.json().get('result'):
                return True
        return False
