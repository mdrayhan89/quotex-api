import requests
import time
from flask import Flask, jsonify, request
from collections import OrderedDict

app = Flask(__name__)

# আপনার সক্রিয় ক্লাউডফ্লেয়ার লিঙ্ক
CLOUDFLARE_WORKER_URL = "https://quotex-data-bridge.islamrabby655.workers.dev"

@app.route('/')
def get_data():
    pair = request.args.get('pair', default='USDBDT_otc')
    count = request.args.get('count', default=10, type=int)

    try:
        # ক্লাউডফ্লেয়ার থেকে ডাটা আনা হচ্ছে
        worker_res = requests.get(f"{CLOUDFLARE_WORKER_URL}/?pair={pair}&count={count}", timeout=15)
        raw_candles = worker_res.json()
        
        final_data = []
        if isinstance(raw_candles, list):
            for i, c in enumerate(raw_candles):
                o, cl = float(c['open']), float(c['close'])
                color = "green" if cl > o else "red" if cl < o else "doji"
                c_time = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(c['time']))
                
                item = OrderedDict([
                    ("id", str(i + 1)),
                    ("pair", pair),
                    ("timeframe", "M1"),
                    ("candle_time", c_time),
                    ("open", str(o)),
                    ("high", str(c['high'])),
                    ("low", str(c['low'])),
                    ("close", str(cl)),
                    ("volume", str(c.get('v', 0))),
                    ("color", color),
                    ("created_at", c_time)
                ])
                final_data.append(item)

        return jsonify(OrderedDict([
            ("Owner_Developer", "DARK-X-RAYHAN"),
            ("Telegram", "@mdrayhan85"),
            ("success", True if final_data else False),
            ("count", len(final_data)),
            ("data", final_data)
        ]))
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
