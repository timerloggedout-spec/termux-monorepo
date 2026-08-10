import hmac
import hashlib
import time
import requests
from urllib.parse import urlencode

class YobitAPI:
    def __init__(self, api_key, api_secret):
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = "https://yobit.net/tapi"
        self.nonce = int(time.time())

    def _generate_signature(self, params):
        body = urlencode(params)
        return hmac.new(
            self.api_secret.encode(),
            body.encode(),
            hashlib.sha512
        ).hexdigest()

    def trade(self, pair, order_type, amount, rate):
        self.nonce += 1
        params = {
            'method': 'Trade',
            'nonce': self.nonce,
            'pair': pair,
            'type': order_type,
            'amount': str(amount),
            'rate': str(rate)
        }
        headers = {
            'Key': self.api_key,
            'Sign': self._generate_signature(params)
        }
        response = requests.post(self.base_url, data=params, headers=headers)
        return response.json()

    def get_balance(self):
        self.nonce += 1
        params = {
            'method': 'getInfo',
            'nonce': self.nonce
        }
        headers = {
            'Key': self.api_key,
            'Sign': self._generate_signature(params)
        }
        response = requests.post(self.base_url, data=params, headers=headers)
        return response.json()