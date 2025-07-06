from flask import Flask, request
import asyncio
import json
import websockets
from waitress import serve
import threading

app = Flask(__name__)

BOT_TOKEN = "7640189770:AAH01Kw3SGSXVZL6bBVStw4MWpzrCpPchpo"
CHAT_ID = "402100936"

@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def telegram_webhook():
    data = request.get_json()
    if "message" in data and "text" in data["message"]:
        text = data["message"]["text"]
        if text == "/imbalance":
            send_message("DeepLocal: очікуємо сигнал з біржі...")
    return {"ok": True}

def send_message(text):
    import requests
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text}
    requests.post(url, json=payload)

async def analyze_orderbook():
    url = "wss://fstream.binance.com/ws/ethusdt@depth20@100ms"
    async with websockets.connect(url) as ws:
        while True:
            try:
                response = await ws.recv()
                data = json.loads(response)
                bids = data['bids']
                asks = data['asks']
                if len(bids) > 0 and len(asks) > 0:
                    best_bid = float(bids[0][0])
                    best_ask = float(asks[0][0])
                    spread = best_ask - best_bid
                    if spread > 1:
                        send_message(f"📊 Спред зараз: {spread:.2f}")
            except Exception as e:
                print("WebSocket error:", e)
                await asyncio.sleep(5)

def run_websocket():
    asyncio.run(analyze_orderbook())

if __name__ == "__main__":
    threading.Thread(target=run_websocket, daemon=True).start()
    serve(app, host="0.0.0.0", port=8080)
