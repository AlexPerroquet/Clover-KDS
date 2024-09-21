import requests
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

class CloverAPI:
    def __init__(self, api_key, merchant_id):
        self.api_key = api_key
        self.merchant_id = merchant_id
        self.base_url = f"https://api.clover.com/v3/merchants/{merchant_id}"

    def get_headers(self):
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def get_orders(self):
        url = f"{self.base_url}/orders"
        response = requests.get(url, headers=self.get_headers())
        response.encoding = 'utf-8'  # Ensure UTF-8 encoding
        return response.json()

    def get_items(self):
        url = f"{self.base_url}/items"
        response = requests.get(url, headers=self.get_headers())
        response.encoding = 'utf-8'  # Ensure UTF-8 encoding
        return response.json()

    def get_order_line_items(self, order_id):
        url = f"{self.base_url}/orders/{order_id}/line_items"
        response = requests.get(url, headers=self.get_headers())
        response.encoding = 'utf-8'  # Ensure UTF-8 encoding
        return response.json()

# Example usage
if __name__ == "__main__":
    api_key = os.getenv("API_KEY")
    merchant_id = os.getenv("MERCHANT_ID")
    clover = CloverAPI(api_key, merchant_id)

    orders = clover.get_orders()
    print("Orders:", orders)

    items = clover.get_items()
    print("Items:", items)