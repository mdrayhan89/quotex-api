import requests
from flask import Flask, jsonify, request

app = Flask(__name__)

QUOTEX_SOURCE = "https://mrbeaxt.site/Qx/Qx.php"

@app.route('/')
def get_quotex_data():
    pair = request.args.get('pair')
    count = request.args.get('count', default=10, type=int)

    if not pair:
        return jsonify({
            "status": "error",
            "message": "Please provide a pair. Example: /?pair=USDBDT_otc&count=10",
            "Owner": "DARK-X-RAYHAN"
        })

    try:
        response = requests.get(f"{QUOTEX_SOURCE}?pair={pair}&count={count}", timeout=10)
        source_data = response.json()

        final_data = []
        if "data" in source_data:
            for item in source_data["data"]:
                final_data.append({
                    "id": item.get("id"),
                    "pair": pair,
                    "timeframe": item.get("timeframe", "M1"),
                    "candle_time": item.get("candle_time"),
                    "open": item.get("open"),
                    "high": item.get("high"),
                    "low": item.get("low"),
                    "close": item.get("close"),
                    "volume": item.get("volume"),
                    "color": item.get("color"),
                    "created_at": item.get("created_at")
                })

        return jsonify({
            "Owner_Developer": "DARK-X-RAYHAN",
            "Telegram": "@mdrayhan85",
            "Channel": "https://t.me/mdrayhan85",
            "success": True,
            "count": len(final_data),
            "data": final_data
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
