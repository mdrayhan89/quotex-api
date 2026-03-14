import requests
from flask import Flask, jsonify, request
from collections import OrderedDict

app = Flask(name)

# JSON কি-গুলোর সিরিয়াল ঠিক রাখার জন্য এই ফাংশন
def format_candle(item, pair):
    # কালার লজিক ঠিক করা
    open_price = float(item.get("open", 0))
    close_price = float(item.get("close", 0))
    
    if close_price > open_price:
        color = "green"
    elif close_price < open_price:
        color = "red"
    else:
        color = "doji"

    # তোমার ১ নম্বর ছবির সিরিয়াল অনুযায়ী সাজানো
    candle = OrderedDict([
        ("id", str(item.get("id"))),
        ("pair", pair),
        ("timeframe", item.get("timeframe", "M1")),
        ("candle_time", item.get("candle_time")),
        ("open", str(item.get("open"))),
        ("high", str(item.get("high"))),
        ("low", str(item.get("low"))),
        ("close", str(item.get("close"))),
        ("volume", str(item.get("volume"))),
        ("color", color),
        ("created_at", item.get("created_at"))
    ])
    return candle

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
        # সোর্স থেকে ডাটা আনা
        source_url = f"https://mrbeaxt.site/Qx/Qx.php?pair={pair}&count={count}"
        response = requests.get(source_url, timeout=10)
        source_data = response.json()

        final_data = []
        if "data" in source_data:
            for item in source_data["data"]:
                formatted_item = format_candle(item, pair)
                final_data.append(formatted_item)

        # ফাইনাল আউটপুট সাজানো
        output = OrderedDict([
            ("Owner_Developer", "DARK-X-RAYHAN"),
            ("Telegram", "@mdrayhan85"),
            ("Channel", "https://t.me/mdrayhan85"),
            ("success", True),
            ("count", len(final_data)),
            ("data", final_data)
        ])

        return jsonify(output)

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

if name == 'main':
    app.run(host='0.0.0.0', port=5000)
