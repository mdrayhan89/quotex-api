import time
import json
import requests
from flask import Flask, jsonify, request
from collections import OrderedDict

app = Flask(__name__)

# সরাসরি Quotex থেকে ডাটা আনার ফাংশন
def get_realtime_candles(pair, count):
    # Quotex-এর ডাটা প্রোভাইডার সোর্স (উদাহরণস্বরূপ একটি স্টেবল সোর্স ব্যবহার করা হয়েছে)
    # সরাসরি ব্রোকার থেকে ডাটা ফেচ করার লজিক
    url = f"https://k-line.quotex.io/api/v1/candles?pair={pair.replace('_otc', '').upper()}&count={count}&timeframe=60"
    
    try:
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Referer": "https://qxbroker.com/"
        }
        response = requests.get(url, headers=headers, timeout=10)
        candles = response.json()
        
        formatted_list = []
        for i, candle in enumerate(candles):
            # কালার লজিক
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
                ("volume", str(candle.get('volume', 0))),
                ("color", color),
                ("created_at", c_time)
            ])
            formatted_list.append(item)
        return formatted_list
    except:
        return []

@app.route('/')
def main_api():
    pair = request.args.get('pair')
    count = request.args.get('count', default=10, type=int)

    if not pair:
        return jsonify({"Owner": "DARK-X-RAYHAN", "message": "Provide a pair name."})

    data = get_realtime_candles(pair, count)
    
    output = OrderedDict([
        ("Owner_Developer", "DARK-X-RAYHAN"),
        ("Telegram", "@mdrayhan85"),
        ("Channel", "https://t.me/mdrayhan85"),
        ("success", True if data else False),
        ("count", len(data)),
        ("data", data)
    ])
    
    return jsonify(output)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
