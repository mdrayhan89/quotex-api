import cloudscraper
import time
from flask import Flask, jsonify, request
from collections import OrderedDict

app = Flask(__name__)

# বাইপাস করার জন্য স্ক্র্যাপার সেটআপ
scraper = cloudscraper.create_scraper(
    browser={
        'browser': 'chrome',
        'platform': 'windows',
        'desktop': True
    }
)

@app.route('/')
def main_api():
    pair = request.args.get('pair', default='USDBDT_otc')
    count = request.args.get('count', default=10, type=int)
    
    # শুধু পেয়ারের নাম নেওয়া (যেমন: USDBDT)
    symbol = pair.split('_')[0].upper()
    
    # বিকল্প এপিআই এন্ডপয়েন্ট (এটি ট্রাই করুন)
    target_url = f"https://qxbroker.com/api/v1/candles?pair={symbol}&count={count}&timeframe=60"

    try:
        response = scraper.get(target_url, timeout=20)
        
        if response.status_code != 200:
            return jsonify({
                "success": False, 
                "error": f"Server status {response.status_code}",
                "msg": "Quotex is blocking this IP"
            })
            
        candles = response.json()
        final_data = []

        if isinstance(candles, list):
            for i, c in enumerate(candles):
                o, cl = float(c['open']), float(c['close'])
                color = "green" if cl > o else "red" if cl < o else "doji"
                
                item = OrderedDict([
                    ("id", str(i + 1)),
                    ("pair", pair),
                    ("open", str(o)),
                    ("high", str(c['high'])),
                    ("low", str(c['low'])),
                    ("close", str(cl)),
                    ("color", color),
                    ("time", time.strftime('%H:%M:%S', time.gmtime(c['time'])))
                ])
                final_data.append(item)

        return jsonify(OrderedDict([
            ("Owner_Developer", "DARK-X-RAYHAN"),
            ("success", True if final_data else False),
            ("data", final_data)
        ]))

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
