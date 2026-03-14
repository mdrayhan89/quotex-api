import requests
import json
import time
from flask import Flask, jsonify, request
from collections import OrderedDict

app = Flask(__name__)

def fetch_quotex_data(pair, count):
    symbol = pair.split('_')[0].upper()
    # সরাসরি কোটেক্সের ক্যান্ডেল সোর্স
    target_url = f"https://k-line.quotex.io/api/v1/candles?pair={symbol}&count={count}&timeframe=60"
    
    # একটি শক্তিশালী পাবলিক প্রক্সি গেটওয়ে ব্যবহার করা হচ্ছে
    proxy_url = f"https://api.allorigins.win/get?url={requests.utils.quote(target_url)}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    }

    try:
        response = requests.get(proxy_url, headers=headers, timeout=20)
        if response.status_code == 200:
            raw_content = response.json().get('contents')
            return json.loads(raw_content)
        return []
    except Exception as e:
        print(f"Error fetching data: {e}")
        return []

@app.route('/')
def rayhan_api():
    pair = request.args.get('pair')
    count = request.args.get('count', default=10, type=int)

    if not pair:
        return jsonify({
            "Owner_Developer": "DARK-X-RAYHAN",
            "status": "Online",
            "message": "Please add ?pair=USDBDT_otc to the URL"
        })

    raw_candles = fetch_quotex_data(pair, count)
    
    final_data = []
    if raw_candles and isinstance(raw_candles, list):
        for i, c in enumerate(raw_candles):
            open_p, close_p = float(c['open']), float(c['close'])
            color = "green" if close_p > open_p else "red" if close_p < open_p else "doji"
            
            # তোমার ১ নম্বর স্ক্রিনশটের সিরিয়াল অনুযায়ী সাজানো
            item = OrderedDict([
                ("id", str(i + 1)),
                ("pair", pair),
                ("timeframe", "M1"),
                ("candle_time", time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(c['time']))),
                ("open", str(open_p)),
                ("high", str(c['high'])),
                ("low", str(c['low'])),
                ("close", str(close_p)),
                ("volume", str(c.get('v', 0))),
                ("color", color),
                ("created_at", time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(c['time'])))
            ])
            final_data.append(item)

    return jsonify(OrderedDict([
        ("Owner_Developer", "DARK-X-RAYHAN"),
        ("Telegram", "@mdrayhan85"),
        ("success", True if final_data else False),
        ("count", len(final_data)),
        ("data", final_data)
    ]))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
