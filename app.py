import time
import json
import websocket
from flask import Flask, jsonify, request
from collections import OrderedDict
import threading

app = Flask(__name__)

# গ্লোবাল ভেরিয়েবল ডাটা স্টোর করার জন্য
latest_candles = []

def get_data_from_ws(pair, count):
    # pair format: usdbdt_otc -> usdbdt
    symbol = pair.split('_')[0].lower()
    ws_url = "wss://ws2.qxbroker.com/socket.io/?EIO=3&transport=websocket"
    
    try:
        ws = websocket.create_connection(ws_url, timeout=10)
        # Quotex-এর সাথে কানেক্ট করার প্রাথমিক মেসেজ (প্রটোকল অনুযায়ী)
        ws.send('42["history",{"symbol":"' + symbol + '","resolution":60,"count":' + str(count) + '}]')
        
        # ডাটা রিসিভ করা
        result = ws.recv()
        ws.close()
        
        # মেসেজ থেকে JSON অংশ আলাদা করা
        if "history" in result:
            json_str = result[result.find('['):]
            data = json.loads(json_str)
            return data[1] # ক্যান্ডেল লিস্ট
        return []
    except Exception as e:
        print(f"Error: {e}")
        return []

@app.route('/')
def api_response():
    pair = request.args.get('pair')
    count = request.args.get('count', default=10, type=int)

    if not pair:
        return jsonify({"Owner": "DARK-X-RAYHAN", "message": "Provide pair name."})

    raw_candles = get_data_from_ws(pair, count)
    
    final_data = []
    if raw_candles:
        for i, candle in enumerate(raw_candles):
            open_p = candle['open']
            close_p = candle['close']
            color = "green" if close_p > open_p else "red" if close_p < open_p else "doji"
            
            c_time = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(candle['time']))
            
            item = OrderedDict([
                ("id", str(i + 1)),
                ("pair", pair),
                ("timeframe", "M1"),
                ("candle_time", c_time),
                ("open", str(open_p)),
                ("high", str(candle['high'])),
                ("low", str(candle['low'])),
                ("close", str(close_p)),
                ("volume", str(candle.get('v', 0))),
                ("color", color),
                ("created_at", c_time)
            ])
            final_data.append(item)

    output = OrderedDict([
        ("Owner_Developer", "DARK-X-RAYHAN"),
        ("Telegram", "@mdrayhan85"),
        ("Channel", "https://t.me/mdrayhan85"),
        ("success", True if final_data else False),
        ("count", len(final_data)),
        ("data", final_data)
    ])
    
    return jsonify(output)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
