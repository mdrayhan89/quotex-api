import requests
import time
from flask import Flask, jsonify, request
from collections import OrderedDict

app = Flask(__name__)

def fetch_candles(pair, count):
    # pair ফরম্যাট হ্যান্ডলিং (যেমন: usdbdt_otc -> USDBDT)
    symbol = pair.split('_')[0].upper()
    
    # ব্যাকআপ সোর্স ১ (কোটেক্স অফিসিয়াল ডাইরেক্ট এপিআই)
    url = f"https://qxbroker.com/api/v1/candles-history/{symbol}/60/{int(time.time()) - (count * 60)}/{int(time.time())}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "application/json",
        "Referer": "https://qxbroker.com/en/demo-trading"
    }

    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            return response.json().get('data', [])
        return []
    except:
        return []

@app.route('/')
def main_api():
    pair = request.args.get('pair')
    count = request.args.get('count', default=10, type=int)

    if not pair:
        return jsonify({"Owner_Developer": "DARK-X-RAYHAN", "message": "Provide a pair name (e.g. USDBDT_otc)"})

    raw_candles = fetch_candles(pair, count)
    
    final_data = []
    if raw_candles:
        # ডাটা যদি অনেক বেশি হয় তবে শুধু কাঙ্ক্ষিত কাউন্ট নেওয়া
        candles_to_process = raw_candles[-count:]
        
        for i, candle in enumerate(candles_to_process):
            open_p = float(candle.get('open'))
            close_p = float(candle.get('close'))
            
            # কালার লজিক
            if close_p > open_p: color = "green"
            elif close_p < open_p: color = "red"
            else: color = "doji"
            
            c_time = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(candle.get('time')))
            
            item = OrderedDict([
                ("id", str(i + 1)),
                ("pair", pair),
                ("timeframe", "M1"),
                ("candle_time", c_time),
                ("open", str(open_p)),
                ("high", str(candle.get('high'))),
                ("low", str(candle.get('low'))),
                ("close", str(close_p)),
                ("volume", str(candle.get('volume', 0))),
                ("color", color),
                ("created_at", c_time)
            ])
            final_data.append(item)

    # তোমার চাওয়া অনুযায়ী আউটপুট
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
