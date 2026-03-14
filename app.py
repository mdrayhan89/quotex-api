import requests
import json
import time
from flask import Flask, jsonify, request
from collections import OrderedDict

app = Flask(__name__)

def fetch_via_backup(pair, count):
    symbol = pair.split('_')[0].upper()
    # ব্যাকআপ সোর্স যা ব্লক হওয়ার সম্ভাবনা কম
    url = f"https://k-line.quotex.io/api/v1/candles?pair={symbol}&count={count}&timeframe=60"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
        "Referer": "https://qxbroker.com/",
        "Accept": "*/*"
    }

    try:
        # সরাসরি কানেকশন ট্রাই
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            return response.json()
        
        # যদি প্রথমটা কাজ না করে তবে দ্বিতীয় ব্যাকআপ
        alt_url = f"https://api.allorigins.win/get?url={requests.utils.quote(url)}"
        alt_res = requests.get(alt_url, timeout=10)
        if alt_res.status_code == 200:
            payload = json.loads(alt_res.json()['contents'])
            return payload
    except:
        return []
    return []

@app.route('/')
def get_data():
    pair = request.args.get('pair')
    count = request.args.get('count', default=10, type=int)

    if not pair:
        return jsonify({"Owner": "DARK-X-RAYHAN", "message": "Add ?pair=SYMBOL to URL"})

    raw_candles = fetch_via_backup(pair, count)
    
    final_data = []
    if raw_candles and isinstance(raw_candles, list):
        for i, c in enumerate(raw_candles):
            o, cl = float(c['open']), float(c['close'])
            color = "green" if cl > o else "red" if cl < o else "doji"
            
            item = OrderedDict([
                ("id", str(i + 1)),
                ("pair", pair),
                ("timeframe", "M1"),
                ("candle_time", time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(c['time']))),
                ("open", str(o)),
                ("high", str(c['high'])),
                ("low", str(c['low'])),
                ("close", str(cl)),
                ("volume", str(c.get('v', 0))),
                ("color", color)
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
