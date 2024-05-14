from flask import Flask, request, jsonify
from flask_cors import CORS
import yfinance as yf
from waitress import serve

app = Flask(__name__)
CORS(app)

# Define a dictionary to store authorized API keys
authorized_keys = {
    "12f5f96f-6b51-4b4a-9bf9-b23e6d728b39": "admin"
}

def calculate_resistance_support(previous_close, real_time_price):
    resistance1 = (previous_close ** 0.5 + 0.125) ** 2
    resistance2 = (previous_close ** 0.5 + 0.25) ** 2
    resistance3 = (previous_close ** 0.5 + 0.5) ** 2
    support1 = (previous_close ** 0.5 - 0.125) ** 2
    support2 = (previous_close ** 0.5 - 0.25) ** 2
    support3 = (previous_close ** 0.5 - 0.5) ** 2
    percentage_change = ((real_time_price - previous_close) / previous_close) * 100
    return resistance1, resistance2, resistance3, support1, support2, support3, percentage_change

@app.route('/stock', methods=['GET'])
def get_stock_price():
    api_key = request.args.get('api_key')
    if api_key not in authorized_keys:
        return jsonify({'error': 'Unauthorized access'}), 401

    stock_name = request.args.get('name')

    if not stock_name:
        return jsonify({'error': 'Stock name not provided'}), 400
    
    # Append ".NS" to the stock name
    nse_stock = f"{stock_name.upper()}.NS"

    try:
        stock_data = yf.Ticker(nse_stock)
        # Fetch data for the last two trading days
        historical_data = stock_data.history(period='2d')
        # Extract the closing price for the previous trading day
        previous_close = historical_data.iloc[-2]['Close']
        # Fetch full name of the stock
        stock_full_name = stock_data.info['longName']

        # Get real-time data
        real_time_data = stock_data.history(period='1d')

        # Extract real-time price
        real_time_price = real_time_data.iloc[-1]['Close']
        # Extract other information
        open_price = real_time_data.iloc[-1]['Open']
        high = real_time_data.iloc[-1]['High']
        low = real_time_data.iloc[-1]['Low']
        fifty_two_week_high = stock_data.info.get('fiftyTwoWeekHigh')
        fifty_two_week_low = stock_data.info.get('fiftyTwoWeekLow')
        volume = real_time_data.iloc[-1]['Volume']
        market_cap = stock_data.info.get('marketCap')

        # Convert market cap to crores
        market_cap_in_crores = market_cap / 1e7

        # Calculate resistance and support levels
        resistance1, resistance2, resistance3, support1, support2, support3, percentage_change = calculate_resistance_support(previous_close, real_time_price)

        return jsonify({
            'Percentage_Change': percentage_change,
            'real_time_price': real_time_price,
            'open_price': open_price,
            'high': high,
            'low': low,
            'fifty_two_week_high': fifty_two_week_high,
            'fifty_two_week_low': fifty_two_week_low,
            'volume': volume,
            'market_cap_in_crores': market_cap_in_crores,
            'stock_full_name': stock_full_name,
            'stock_name': stock_name,  # Returning the modified stock name with ".NS"
            'previous_close': previous_close,
            'resistance1': resistance1,
            'resistance2': resistance2,
            'resistance3': resistance3,
            'support1': support1,
            'support2': support2,
            'support3': support3
            
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Use Waitress as the production WSGI server
    serve(app, host='0.0.0.0', port=50100)
