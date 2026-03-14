import cloudscraper
import time
from flask import Flask, jsonify, request
from collections import OrderedDict

app = Flask(__name__)

# এটি কোটেক্সের সিকিউরিটি বাইপাস করতে সাহায্য করবে
scraper = cloudscraper.create_scraper()

@app.route('/')
def get_data():
    pair = request.args.get('pair', default='USDBDT_otc')
    count = request.args.get('count', default=10, type=int)
    
    # পেয়ার ফরম্যাট ঠিক করা
    symbol = pair.split('_')[0].upper()
    target_url = f"https://k-line.quotex.io/api/v1/candles?pair={symbol}&count={count}&timeframe=60"

    try:
        response = scraper.get(target_url, timeout=15)
        if response.status_code != 200:
            return jsonify({"success": False, "error": "Quotex blocked direct access"})
            
        candles = response.json()
        final_data = []

        if isinstance(candles, list):
            for i, c in enumerate(candles):
                o, cl = float(c['open']), float(c['close'])
                color = "green" if cl > o else "red" if cl < o else "doji"
                c_time = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(c['time']))
                
                item = OrderedDict([
                    ("id", str(i + 1)),
                    ("pair", pair),
                    ("open", str(o)),
                    ("high", str(c['high'])),
                    ("low", str(c['low'])),
                    ("close", str(cl)),
                    ("color", color),
                    ("time", c_time)
                ])
                final_data.append(item)

        return jsonify(OrderedDict([
            ("Owner_Developer", "DARK-X-RAYHAN"),
            ("success", True if final_data else False),
            ("count", len(final_data)),
            ("data", final_data)
        ]))

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
