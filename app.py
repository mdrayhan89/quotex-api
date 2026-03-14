import cloudscraper
import time
from flask import Flask, jsonify, request
from collections import OrderedDict

app = Flask(__name__)

# কোটেক্স বাইপাস করার জন্য বিশেষ স্ক্র্যাপার
scraper = cloudscraper.create_scraper(
    browser={
        'browser': 'chrome',
        'platform': 'windows',
        'desktop': True
    }
)

@app.route('/')
def main_api():
    # সরাসরি কোটেক্সের ডাটাবেজ থেকে ডাটা আনার চেষ্টা
    pair = request.args.get('pair', default='USDBDT_otc')
    count = request.args.get('count', default=10, type=int)
    
    symbol = pair.split('_')[0].upper()
    # আমরা সরাসরি এই লিঙ্কটি ব্যবহার করব যা ব্লক হওয়ার সম্ভাবনা কম
    url = f"https://qxbroker.com/api/v1/candles?pair={symbol}&count={count}&timeframe=60"

    try:
        response = scraper.get(url, timeout=25)
        
        if response.status_code != 200:
            return jsonify({
                "Owner": "DARK-X-RAYHAN",
                "success": False, 
                "error": f"Status Code: {response.status_code}",
                "note": "Please try again after 1 minute"
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
            ("success": True),
            ("data", final_data)
        ]))

    except Exception as e:
        return jsonify({"success": False, "error": "Server is busy", "details": str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
