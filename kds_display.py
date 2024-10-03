import json
import logging
import time
from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
from clover_api import CloverAPI
from dotenv import load_dotenv
import os
import datetime
import pytz
from unidecode import unidecode

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
socketio = SocketIO(app)

API_KEY = os.getenv("API_KEY")
MERCHANT_ID = os.getenv("MERCHANT_ID")

clover = CloverAPI(API_KEY, MERCHANT_ID)

logging.basicConfig(level=logging.DEBUG)

last_fetch_time = 0

# In-memory store for completed orders
completed_orders = {}

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

def convert_unix_to_human_readable(unix_timestamp):
    created_time_seconds = unix_timestamp / 1000
    utc_time = datetime.datetime.fromtimestamp(created_time_seconds, pytz.UTC)
    local_tz = pytz.timezone('US/Eastern')
    local_time = utc_time.astimezone(local_tz)
    return local_time.strftime('%d-%b-%Y %H:%M')

def is_order_from_today(unix_timestamp):
    created_time_seconds = unix_timestamp / 1000
    utc_time = datetime.datetime.fromtimestamp(created_time_seconds, pytz.UTC)
    local_tz = pytz.timezone('US/Eastern')
    local_time = utc_time.astimezone(local_tz)
    today = datetime.datetime.now(local_tz).date()
    return local_time.date() == today

@app.route('/')
def display_orders():
    return render_template('orders.html')

@app.route('/api/orders')
def api_orders():
    global last_fetch_time
    orders = clover.get_orders()
    
    # Sort orders by creation time and get the latest 10 orders
    orders['elements'].sort(key=lambda x: x['createdTime'], reverse=True)
    recent_orders = orders['elements'][:10]
    
    filtered_orders = [order for order in recent_orders if is_order_from_today(order['createdTime'])]
    
    for order in filtered_orders:
        order['line_items'] = get_order_line_items_with_retry(order['id'])
        
        if 'elements' in order['line_items']:
            for item in order['line_items']['elements']:
                if 'modifications' in item:
                    for mod in item['modifications']['elements']:
                        mod['name'] = unidecode(mod['name'])
        
        # Convert the createdTime to a human-readable format
        order['createdTimeHumanReadable'] = convert_unix_to_human_readable(order['createdTime'])
        # Include the raw createdTime for calculating elapsed time
        order['createdTimeRaw'] = order['createdTime']

    last_fetch_time = int(time.time() * 1000)  # Update last fetch time to current time in milliseconds
    
    return json.dumps({'elements': filtered_orders})

@app.route('/api/completed_orders', methods=['GET', 'POST'])
def api_completed_orders():
    if request.method == 'POST':
        data = request.json
        order_id = data['order_id']
        item_id = data['item_id']
        completed = data['completed']
        
        if order_id not in completed_orders:
            completed_orders[order_id] = set()
        
        if completed:
            completed_orders[order_id].add(item_id)
        else:
            completed_orders[order_id].discard(item_id)
        
        # Emit the update to all connected clients
        socketio.emit('update_completed_orders', {'order_id': order_id, 'item_id': item_id, 'completed': completed})
        
        return json.dumps({'status': 'success'})
    
    elif request.method == 'GET':
        # Convert sets to lists for JSON serialization
        serializable_completed_orders = {order_id: list(item_ids) for order_id, item_ids in completed_orders.items()}
        return json.dumps(serializable_completed_orders)

if __name__ == "__main__":
    socketio.run(app, host='0.0.0.0', port=5000, debug=False, allow_unsafe_werkzeug=True)