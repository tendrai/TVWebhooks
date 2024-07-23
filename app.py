import asyncio
from flask import Flask, request, jsonify
import os
from binance.client import Client
from binance.enums import *

app = Flask(__name__)

# Configure Binance API
binance_api_key = os.environ.get('BINANCE_API_KEY')
binance_api_secret = os.environ.get('BINANCE_API_SECRET')
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
    order = None  # Initialize order variable
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
                                        side=SIDE_BUY,
                                        type=ORDER_TYPE_MARKET,
                                        quantity=order_size)
    elif action == 'sell':
        if current_position_size > 0:
            # Close current long position
            print(f"Closing long position of size: {abs(current_position_size)}")
            await asyncio.to_thread(client.futures_create_order,
                                    symbol=ticker,
                                    side=SIDE_SELL,
                                    type=ORDER_TYPE_MARKET,
                                    quantity=abs(current_position_size))
        # Open short position
        print(f"Opening short position of size: {order_size}")
        order = await asyncio.to_thread(client.futures_create_order,
                                        symbol=ticker,
                                        side=SIDE_SELL,
                                        type=ORDER_TYPE_MARKET,
                                        quantity=order_size)

    return jsonify(order)

if __name__ == '__main__':
    app.run(debug=True)
