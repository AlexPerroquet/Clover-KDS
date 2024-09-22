import json
import logging
import time
from flask import Flask, render_template
from clover_api import CloverAPI
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

API_KEY = os.getenv("API_KEY")
MERCHANT_ID = os.getenv("MERCHANT_ID")

clover = CloverAPI(API_KEY, MERCHANT_ID)

logging.basicConfig(level=logging.DEBUG)

last_fetch_time = 0

def get_order_line_items_with_retry(order_id, retries=5, backoff_in_seconds=1):
    for i in range(retries):
        response = clover.get_order_line_items(order_id)
        if 'message' in response and response['message'] == "429 Too Many Requests":
            logging.warning(f"Rate limit hit for order ID: {order_id}. Retrying in {backoff_in_seconds} seconds...")
            time.sleep(backoff_in_seconds)
            backoff_in_seconds *= 2  # Exponential backoff
        else:
            return response
    logging.error(f"Failed to get line items for order ID: {order_id} after {retries} retries.")
    return {}

@app.route('/')
def display_orders():
    return render_template('orders.html')

@app.route('/api/orders')
def api_orders():
    global last_fetch_time
    orders = clover.get_orders()
    
    # Sort orders by creation time and get the latest 20 orders
    orders['elements'].sort(key=lambda x: x['createdTime'], reverse=True)
    recent_orders = orders['elements'][:10]
    
    for order in recent_orders:
        order['line_items'] = get_order_line_items_with_retry(order['id'])
        
        if 'elements' in order['line_items']:
            for item in order['line_items']['elements']:
                item['name'] = item['name'].encode('ascii', 'ignore').decode('ascii')

    last_fetch_time = int(time.time() * 1000)  # Update last fetch time to current time in milliseconds
    return json.dumps({'elements': recent_orders})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=False)