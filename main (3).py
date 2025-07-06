
import asyncio
import json
import requests
import websockets
from flask import Flask, request
from threading import Thread
from waitress import serve

app = Flask(__name__)

BOT_TOKEN = "7640189770:AAH01Kw3SGSXVZL6bBVStw4MWpzrCpPchpo"
CHAT_ID = "402100936"
IMBALANCE_THRESHOLD_PERCENT = 1.0

def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "HTML"
    }
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"Telegram send error: {e}")

@app.route('/')
def index():
    return "DeepLocal Webhook is running."

@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    data = request.get_json()
    if "message" in data and "text" in data["message"]:
        if data["message"]["text"] == "/imbalance":
            send_telegram_message("DeepLocal: очікуємо сигнал з біржі...")
    return {"ok": True}

async def analyze_orderbook():
    url = "wss://fstream.binance.com/ws/ethusdt@depth@100ms"
    async with websockets.connect(url) as ws:
        while True:
            response = await ws.recv()
            data = json.loads(response)

            bids = data.get("b", [])
            asks = data.get("a", [])

            if not bids or not asks:
                continue

            top_bid = float(bids[0][1])
            top_ask = float(asks[0][1])

            if top_ask == 0:
                continue

            diff = abs(top_bid - top_ask)
            percent_diff = (diff / top_ask) * 100

            if percent_diff > IMBALANCE_THRESHOLD_PERCENT:
                msg = f"📊 DeepLocal Signal:
Обʼємний дисбаланс {percent_diff:.2f}% між bid/ask"
                send_telegram_message(msg)

def start_websocket():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(analyze_orderbook())

if __name__ == "__main__":
    Thread(target=start_websocket).start()
    serve(app, host="0.0.0.0", port=8080)
