import requests
import time
from flask import Flask, jsonify, request
from collections import OrderedDict

app = Flask(__name__)

def fetch_data(pair, count):
    # pair format handle
    symbol = pair.split('_')[0].upper()
    # একটি গ্লোবাল পাবলিক এপিআই প্রক্সি যা কোটেক্স ডাটা রিড করতে পারে
    url = f"https://api.allorigins.win/get?url={requests.utils.quote(f'https://qxbroker.com/api/v1/candles-history/{symbol}/60/{int(time.time())-600}/{int(time.time())}')}"
    
    try:
        response = requests.get(url, timeout=15)
        raw_data = response.json()
        contents = json.loads(raw_data['contents'])
        return contents.get('data', [])
    except:
        # যদি প্রক্সি ফেইল করে তবে সরাসরি ট্রাই করবে
        try:
            direct_url = f"https://k-line.quotex.io/api/v1/candles?pair={symbol}&count={count}&timeframe=60"
            res = requests.get(direct_url, timeout=10)
            return res.json()
        except:
            return []

@app.route('/')
def rayhan_api():
    pair = request.args.get('pair')
    count = request.args.get('count', default=10, type=int)

    if not pair:
        return jsonify({"Owner": "DARK-X-RAYHAN", "status": "active"})

    # ডাটা আনা হচ্ছে
    candles = fetch_data(pair, count)
    
    final_data = []
    if candles:
        for i, c in enumerate(candles[-count:]):
            o, c_p = float(c['open']), float(c['close'])
            color = "green" if c_p > o else "red" if c_p < o else "doji"
            
            item = OrderedDict([
                ("id", str(i + 1)),
                ("pair", pair),
                ("timeframe", "M1"),
                ("open", str(o)),
                ("high", str(c['high'])),
                ("low", str(c['low'])),
                ("close", str(c_p)),
                ("color", color),
                ("candle_time", time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(c['time'])))
            ])
            final_data.append(item)

    return jsonify(OrderedDict([
        ("Owner_Developer", "DARK-X-RAYHAN"),
        ("success", True if final_data else False),
        ("count", len(final_data)),
        ("data", final_data)
    ]))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
