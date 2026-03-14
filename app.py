import cloudscraper
import time
from flask import Flask, jsonify, request
from collections import OrderedDict

app = Flask(__name__)

def fetch_quotex_data(pair, count):
    # কারেন্সি ফরম্যাট ঠিক করা
    symbol = pair.split('_')[0].upper()
    url = f"https://k-line.quotex.io/api/v1/candles?pair={symbol}&count={count}&timeframe=60"
    
    # এটি ব্রাউজারের মতো অভিনয় করে ডাটা নিয়ে আসবে
    scraper = cloudscraper.create_scraper()
    
    try:
        response = scraper.get(url, timeout=15)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception:
        return None

@app.route('/')
def api_response():
    pair = request.args.get('pair', default='USDBDT_otc')
    count = request.args.get('count', default=10, type=int)

    candles = fetch_quotex_data(pair, count)
    
    if not candles:
        return jsonify({
            "Owner_Developer": "DARK-X-RAYHAN",
            "success": False,
            "message": "Data Source Blocked or Invalid Pair"
        })

    final_data = []
    for i, c in enumerate(candles):
        o, cl = float(c['open']), float(c['close'])
        color = "green" if cl > o else "red" if cl < o else "doji"
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(c['time']))
        
        item = OrderedDict([
            ("id", str(i + 1)),
            ("pair", pair),
            ("open", str(o)),
            ("high", str(c['high'])),
            ("low", str(c['low'])),
            ("close", str(cl)),
            ("color", color),
            ("candle_time", timestamp)
        ])
        final_data.append(item)

    return jsonify(OrderedDict([
        ("Owner_Developer", "DARK-X-RAYHAN"),
        ("success": True),
        ("count", len(final_data)),
        ("data", final_data)
    ]))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
