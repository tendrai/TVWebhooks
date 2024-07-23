import asyncio
from flask import Flask, request, jsonify
import os
from binance.client import Client
from binance.enums import *

app = Flask(__name__)

# Configure Binance API
binance_api_key = os.environ.get('yOWkYTnsMYKEZcQW5tI6D7oqdHwystJ2hSuyrPWPHdER4bafK9a0OWbfDg4eko66')
binance_api_secret = os.environ.get('Kj0KQ8bixe4rmaC2ZWYxd9yd8a7AWMPEKJtf73Ltof9TqtPLNlniz6WwuhCR7Bok')
client = Client(binance_api_key, binance_api_secret)


@app.route('/')
def index():
    return "Hello, this is the home page!"


@app.route('/webhook', methods=['POST'])
async def webhook():
    data = request.json
    print(data)  # Log the received data

    # Extract details from the webhook payload
    action = data.get('action')
    ticker = data.get('ticker', 'ONEUSDT') + ".P"
    leverage = data.get('leverage', 10)
    funds_percentage = data.get('funds_percentage', 10)

    # Set leverage
    await asyncio.to_thread(client.futures_change_leverage, symbol=ticker, leverage=leverage)

    # Get account balance
    balance_info = await asyncio.to_thread(client.futures_account_balance)
    usdt_balance = next(item for item in balance_info if item['asset'] == 'USDT')['balance']
    usdt_balance = float(usdt_balance)

    # Calculate order size
    order_size = (usdt_balance * funds_percentage / 100) * leverage
    print(f"Calculated order size: {order_size}")

    # Check current position
    positions = await asyncio.to_thread(client.futures_account)
    current_position_size = 0
    for position in positions['positions']:
        if position['symbol'] == ticker:
            current_position_size = float(position['positionAmt'])
            print(f"Current position size for {ticker}: {current_position_size}")
            break

    # Perform actions based on the current position and desired action
    if action == 'buy':
        if current_position_size < 0:
            # Close current short position
            print(f"Closing short position of size: {abs(current_position_size)}")
            await asyncio.to_thread(client.futures_create_order,
                                    symbol=ticker,
                                    side=SIDE_BUY,
                                    type=ORDER_TYPE_MARKET,
                                    quantity=abs(current_position_size))
        # Open long position
        print(f"Opening long position of size: {order_size}")
        order = await asyncio.to_thread(client.futures_create_order,
                                        symbol=ticker,
                                        side=SI
