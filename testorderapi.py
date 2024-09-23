import os
import time
import requests
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class CloverAPI:
    def __init__(self, api_key, merchant_id):
        self.api_key = api_key
        self.merchant_id = merchant_id
        self.base_url = "https://api.clover.com/v3/merchants/"

    def fetch_with_retry(self, fetch_function, *args, max_retries=3, retry_delay=2):
        retries = 0
        while retries < max_retries:
            response = fetch_function(*args)
            if response.get('message') == "429 Too Many Requests":
                retries += 1
                time.sleep(retry_delay)
            else:
                return response
        return response

    def get_order_details(self, order_id):
        url = f"{self.base_url}/{self.merchant_id}/orders/{order_id}"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        print(f"Requesting order details with headers: {headers}")  # Debugging line
        response = requests.get(url, headers=headers)
        return response.json()

    def get_modifiers(self, order_id, line_item_id):
        url = f"{self.base_url}/{self.merchant_id}/orders/{order_id}/line_items/{line_item_id}/modifications"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        print(f"Requesting modifiers with headers: {headers}")  # Debugging line
        response = requests.get(url, headers=headers)
        return response.json()

    def get_order_with_modifiers(self, order_id):
        # Fetch the order details with retry logic
        order = self.fetch_with_retry(self.get_order_details, order_id)
        
        # Check if the order contains line items
        if 'elements' in order:
            for line_item in order['elements']:
                # Fetch the modifiers for each line item with retry logic
                line_item_id = line_item['id']
                modifiers = self.fetch_with_retry(self.get_modifiers, order_id, line_item_id)
                # Append the modifiers to the line item
                line_item['modifiers'] = modifiers
        
        return order

# Load environment
api_key = os.getenv("API_KEY")
merchant_id = os.getenv("MERCHANT_ID")

# Print the loaded environment variables for debugging
print(f"API_KEY: {api_key}")  # Debugging line
print(f"MERCHANT_ID: {merchant_id}")  # Debugging line

# Check if API key and merchant ID are set
if not api_key or not merchant_id:
    raise ValueError("API key and Merchant ID must be set in the environment variables.")

# Create an instance of CloverAPI
clover = CloverAPI(api_key, merchant_id)

# Fetch order details using the new method
order_id = input("Enter the Order ID\n")
order = clover.get_order_with_modifiers(order_id)

# Combine all information into a single dictionary
combined_data = {
    "order_details": order,
}

# Create the subfolder if it doesn't exist
os.makedirs("Json_Respond", exist_ok=True)

# Save the combined data to a JSON file
output_file = os.path.join("Json_Respond", "combined_order_data.json")
with open(output_file, "w") as f:
    json.dump(combined_data, f, indent=4)

print(f"Order data with modifiers saved to {output_file}")