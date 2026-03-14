import requests
import time
from flask import Flask, jsonify, request
from collections import OrderedDict

app = Flask(__name__)

def get_live_data(pair, count):
    # কোটেক্সের ডাটা প্রোভাইডার মেথড
    symbol = pair.split('_')[0].upper()
    
    # এটি একটি পাবলিক গেটওয়ে যা কোটেক্স ডাটা রিড করতে পারে
    # যদি এটি ব্লক হয়, আমরা ডাইনামিক সোর্স ব্যবহার করব
    url = f"https://k-line.quotex.io/api/v1/candles?pair={symbol}&count={count}&timeframe=60"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Referer": "https://qxbroker.com/"
    }

    try:
        # আমরা সরাসরি সোর্স থেকে ডাটা আনার সর্বোচ্চ চেষ্টা করছি
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            return response.json()
        
        # ব্যাকআপ সোর্স যদি মেইনটা ফেইল করে
        backup_url = f"https://api.allorigins.win/get?url={requests.utils.quote(url)}"
        backup_res = requests.get(backup_url, timeout=15)
        if backup_res.status_code == 200:
            import json
            data = json.loads(backup_res.json()['contents'])
            return data
    except:
        return []
    return []

@app.route('/')
def rayhan_api():
    pair = request.args.get('pair')
    count = request.args.get('count', default=10, type=int)

    if not pair:
        return jsonify({"Owner": "DARK-X-RAYHAN", "status": "Online", "msg": "Add ?pair=USDBDT_otc"})

    raw_data = get_live_data(pair, count)
    
    final_data = []
    if raw_data and isinstance(raw_data, list):
        for i, c in enumerate(raw_data):
            o, cl = float(c['open']), float(c['close'])
            color = "green" if cl > o else "red" if cl < o else "doji"
            
            # তোমার ১ নম্বর ছবির সেই সিরিয়াল অনুযায়ী সাজানো
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
                ("color", color),
                ("created_at", time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(c['time'])))
            ])
            final_data.append(item)

    # রেজাল্ট আউটপুট
    res = OrderedDict([
        ("Owner_Developer", "DARK-X-RAYHAN"),
        ("success", True if final_data else False),
        ("count", len(final_data)),
        ("data", final_data)
    ])
    
    return jsonify(res)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
