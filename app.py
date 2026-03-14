import requests
import time
from flask import Flask, jsonify, request
from collections import OrderedDict

app = Flask(__name__)

def get_quotex_candles(pair, count):
    # Quotex সরাসরি ডাটা সোর্স (পাবলিক)
    # pair ফরম্যাট ঠিক করা (যেমন: USDBDT_otc -> USDBDT)
    clean_pair = pair.split('_')[0].upper()
    
    # এটি সরাসরি কোটেক্সের ক্যান্ডেল ডাটা সোর্স লিঙ্ক
    url = f"https://k-line.quotex.io/api/v1/candles?pair={clean_pair}&count={count}&timeframe=60"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://qxbroker.com/"
    }

    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

@app.route('/')
def main_api():
    pair = request.args.get('pair')
    count = request.args.get('count', default=10, type=int)

    if not pair:
        return jsonify({"message": "Pair name required", "Owner": "DARK-X-RAYHAN"})

    # সরাসরি ডাটা আনা হচ্ছে
    raw_data = get_quotex_candles(pair, count)
    
    final_data = []
    if raw_data:
        for i, candle in enumerate(raw_data):
            # কালার লজিক
            open_p = candle['open']
            close_p = candle['close']
            color = "green" if close_p > open_p else "red" if close_p < open_p else "doji"
            
            # টাইম ফরম্যাট ঠিক করা
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
                ("volume", str(candle.get('volume', 0))),
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
