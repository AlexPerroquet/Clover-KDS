import json
import logging
import time
from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
from clover_api import CloverAPI
from dotenv import load_dotenv
import os
<<<<<<< Updated upstream
=======
import datetime
import pytz

# Try to import unidecode, but provide a fallback if it's not available
try:
    from unidecode import unidecode
except ImportError:
    def unidecode(text):
        return text  # Fallback function that just returns the original text
>>>>>>> Stashed changes

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

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

<<<<<<< Updated upstream
=======
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

@socketio.on('connect')
def handle_connect():
    # Convert sets to lists for JSON serialization
    serializable_orders = {order_id: list(items) for order_id, items in completed_orders.items()}
    emit('init_completed_orders', serializable_orders)

@socketio.on('update_completed_orders')
def handle_update_completed_orders(data):
    order_id = data['order_id']
    item_id = data['item_id']
    completed = data['completed']
    
    if order_id not in completed_orders:
        completed_orders[order_id] = set()
    
    if completed:
        completed_orders[order_id].add(item_id)
    else:
        completed_orders[order_id].discard(item_id)
    
    # Save the updated completed orders
    save_completed_orders()
    
    # Emit the update to all connected clients
    emit('update_completed_orders', {'order_id': order_id, 'item_id': item_id, 'completed': completed}, broadcast=True)

>>>>>>> Stashed changes
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
<<<<<<< Updated upstream
                item['name'] = item['name'].encode('ascii', 'ignore').decode('ascii')
=======
                item_id = item['id']
                item['completed'] = item_id in completed_orders.get(order['id'], set())
>>>>>>> Stashed changes
                if 'modifications' in item:
                    for mod in item['modifications']['elements']:
                        mod['name'] = mod['name'].encode('ascii', 'ignore').decode('ascii')

    last_fetch_time = int(time.time() * 1000)  # Update last fetch time to current time in milliseconds
    return json.dumps({'elements': recent_orders})

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

<<<<<<< Updated upstream
if __name__ == "__main__":
    socketio.run(app, host='0.0.0.0', port=5000, debug=False, allow_unsafe_werkzeug=True)
    
    
=======
def load_completed_orders():
    global completed_orders
    try:
        with open('completed_orders.json', 'r') as f:
            completed_orders = json.load(f)
        # Convert lists back to sets
        for order_id, items in completed_orders.items():
            completed_orders[order_id] = set(items)
    except FileNotFoundError:
        completed_orders = {}

def save_completed_orders():
    with open('completed_orders.json', 'w') as f:
        # Convert sets to lists for JSON serialization
        serializable_orders = {order_id: list(items) for order_id, items in completed_orders.items()}
        json.dump(serializable_orders, f)

if __name__ == '__main__':
    # This block will only be executed when running the script directly
    # It won't be used when running with Gunicorn
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
>>>>>>> Stashed changes
