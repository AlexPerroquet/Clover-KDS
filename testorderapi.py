import requests
import json
from dotenv import load_dotenv
import os
import time

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

    def get_order_details(self, order_id):
        url = f"{self.base_url}/orders/{order_id}"
        response = requests.get(url, headers=self.get_headers())
        return self._parse_response(response)
    
    def get_order_line_items(self, order_id):
        url = f"{self.base_url}/orders/{order_id}/line_items"
        response = requests.get(url, headers=self.get_headers())
        return self._parse_response(response)

    def get_order_type(self, order_type_id):
        url = f"{self.base_url}/order_types/{order_type_id}"
        response = requests.get(url, headers=self.get_headers())
        return self._parse_response(response)

    def get_payments(self, order_id):
        url = f"{self.base_url}/orders/{order_id}/payments"
        response = requests.get(url, headers=self.get_headers())
        return self._parse_response(response)

    def get_modifiers(self, mod_group_id):
        url = f"{self.base_url}/modifier_groups/{mod_group_id}"
        response = requests.get(url, headers=self.get_headers())
        return self._parse_response(response)

    def get_single_modifier(self, mod_group_id, mod_id):
        url = f"{self.base_url}/modifier_groups/{mod_group_id}/modifiers/{mod_id}"
        response = requests.get(url, headers=self.get_headers())
        return self._parse_response(response)

    def get_order_fee_line_items(self, order_id, retries=5, backoff_factor=1):
        url = f"{self.base_url}/orders/{order_id}/order_fee_line_items"
        for retry in range(retries):
            response = requests.get(url, headers=self.get_headers())
            if response.status_code == 429:
                wait_time = backoff_factor * (2 ** retry)
                print(f"Rate limit exceeded. Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                return self._parse_response(response)
        print("Failed to fetch order fee line items after several retries.")
        return {"message": "Failed to fetch order fee line items after several retries."}

    def get_line_item_details(self, order_id, line_item_id):
        url = f"{self.base_url}/orders/{order_id}/line_items/{line_item_id}"
        response = requests.get(url, headers=self.get_headers())
        return self._parse_response(response)

    def get_order(self, order_id):
        url = f"{self.base_url}/orders/{order_id}"
        response = requests.get(url, headers=self.get_headers())
        return self._parse_response(response)

    def get_modifications(self, order_id):
        url = f"{self.base_url}/orders/{order_id}/modifications"
        response = requests.get(url, headers=self.get_headers())
        return self._parse_response(response)

    def _parse_response(self, response):
        try:
            return response.json()
        except json.JSONDecodeError:
            print(f"Failed to parse JSON response: {response.text}")
            return {}

# Example usage
if __name__ == "__main__":
    API_KEY = os.getenv("API_KEY")
    MERCHANT_ID = os.getenv("MERCHANT_ID")
    clover = CloverAPI(API_KEY, MERCHANT_ID)

    order_id = input("Enter the Order ID")
    order_details = clover.get_order_details(order_id)
    order_line_items = clover.get_order_line_items(order_id)

    # Extract order type ID and fetch order type details
    order_type_id = order_details.get("orderType", {}).get("id")
    order_type_details = clover.get_order_type(order_type_id) if order_type_id else {}

    # Fetch payment details
    payment_details = clover.get_payments(order_id)

    # Fetch modifiers for each line item
    modifiers = []
    for item in order_line_items.get("elements", []):
        mod_group_id = item.get("modGroupId")
        if mod_group_id:
            modifiers.append(clover.get_modifiers(mod_group_id))

    # Fetch a single modifier example
    mod_group_id = "exampleModGroupId"
    mod_id = "exampleModId"
    single_modifier = clover.get_single_modifier(mod_group_id, mod_id)

    # Fetch order fee line items
    order_fee_line_items = clover.get_order_fee_line_items(order_id)

    # Fetch details for a specific line item
    line_item_id = "exampleLineItemId"
    line_item_details = clover.get_line_item_details(order_id, line_item_id)

    # Fetch order details using the new method
    order = clover.get_order(order_id)

    # Fetch modifications for the order
    modifications = clover.get_modifications(order_id)

    # Combine all information into a single dictionary
    combined_data = {
        "order_details": order_details,
        "order_line_items": order_line_items,
        "order_type_details": order_type_details,
        "payment_details": payment_details,
        "modifiers": modifiers,
        "single_modifier": single_modifier,
        "order_fee_line_items": order_fee_line_items,
        "line_item_details": line_item_details,
        "order": order,
        "modifications": modifications
    }

    # Create the subfolder if it doesn't exist
    os.makedirs("Json_Respond", exist_ok=True)

    # Save combined data to a single JSON file
    with open("Json_Respond/combined_order_data.json", "w") as f:
        json.dump(combined_data, f, indent=4)

    print("All order information has been saved to Json_Respond/combined_order_data.json")