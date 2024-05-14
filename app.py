from flask import Flask, request, jsonify
from flask_cors import CORS
import yfinance as yf
from waitress import serve

app = Flask(__name__)
CORS(app)

# Define a dictionary to store authorized API keys
authorized_keys = {
    "b0ccdd40-9f04-4916-9309-59cdd76d02b1": "admin"
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
    
    # Check if the stock symbol is "^NSEI" or other supported indexes
    supported_indexes = ["^NSEI", "^NSEBANK", "^BSESN"]
    if stock_name.upper() in supported_indexes:
        try:
            index_data = yf.Ticker(stock_name.upper())
            current_data = index_data.history(period='1d')
            previous_data = index_data.history(period='2d')
            real_time_price = current_data.iloc[-1]['Close']
            previous_close = previous_data.iloc[-2]['Close']
            open_price = current_data.iloc[0]['Open']
            high = current_data['High'].max()
            low = current_data['Low'].min()
            fifty_two_week_high = index_data.info.get('fiftyTwoWeekHigh')
            fifty_two_week_low = index_data.info.get('fiftyTwoWeekLow')
            volume = current_data.iloc[-1]['Volume']
            
            resistance1, resistance2, resistance3, support1, support2, support3, percentage_change = calculate_resistance_support(previous_close, real_time_price)

            return jsonify({
                'percentage_change': percentage_change,
                'real_time_price': real_time_price,
                'previous_close': previous_close,
                'resistance1': resistance1,
                'resistance2': resistance2,
                'resistance3': resistance3,
                'support1': support1,
                'support2': support2,
                'support3': support3,
                'fifty_two_week_high': fifty_two_week_high,
                'fifty_two_week_low': fifty_two_week_low,
                'volume': volume,
                'open': open_price,
                'high': high,
                'low': low
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    # Append ".NS" to the stock name for regular stocks
    nse_stock = f"{stock_name.upper()}.NS"

    try:
        stock_data = yf.Ticker(nse_stock)
        historical_data = stock_data.history(period='2d')
        previous_close = historical_data.iloc[-2]['Close']
        stock_full_name = stock_data.info['longName']

        real_time_data = stock_data.history(period='1d')

        real_time_price = real_time_data.iloc[-1]['Close']
        open_price = real_time_data.iloc[-1]['Open']
        high = real_time_data.iloc[-1]['High']
        low = real_time_data.iloc[-1]['Low']
        fifty_two_week_high = stock_data.info.get('fiftyTwoWeekHigh')
        fifty_two_week_low = stock_data.info.get('fiftyTwoWeekLow')
        volume = real_time_data.iloc[-1]['Volume']
        market_cap = stock_data.info.get('marketCap')

        market_cap_in_crores = market_cap / 1e7

        resistance1, resistance2, resistance3, support1, support2, support3, percentage_change = calculate_resistance_support(previous_close, real_time_price)

        return jsonify({
            'percentage_change': percentage_change,
            'real_time_price': real_time_price,
            'open_price': open_price,
            'high': high,
            'low': low,
            'fifty_two_week_high': fifty_two_week_high,
            'fifty_two_week_low': fifty_two_week_low,
            'volume': volume,
            'market_cap_in_crores': market_cap_in_crores,
            'stock_full_name': stock_full_name,
            'stock_name': stock_name,  # Returning the modified stock name with ".NS" if applicable
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
