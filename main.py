import asyncio
import json
import websockets
import logging
from flask import Flask, request
import telegram
import threading

# Налаштування
TOKEN = "7640189770:AAH01Kw3SGSXVZL6bBVStw4MWpzrCpPchpo"
CHAT_ID = "402100936"
URL_PATH = f"/{TOKEN}"
app = Flask(__name__)
bot = telegram.Bot(token=TOKEN)

# Флаг для запуску WebSocket
ws_started = False

# Обробка webhook
@app.route(URL_PATH, methods=["POST"])
def webhook():
    data = request.get_json()
    if data and "message" in data and "text" in data["message"]:
        text = data["message"]["text"]
        if text == "/imbalance":
            bot.send_message(chat_id=CHAT_ID, text="DeepLocal: очікуємо сигнал з біржі...")
    return "ok"

# Аналіз orderbook
async def analyze_orderbook(message):
    try:
        data = json.loads(message)
        if "b" in data and "a" in data:
            bids = data["b"]
            asks = data["a"]
            if not bids or not asks:
                return
            top_bid = float(bids[0][1])
            top_ask = float(asks[0][1])
            imbalance = round((top_bid - top_ask) / (top_bid + top_ask) * 100, 4)

            print(f"[WS] Imbalance: {imbalance}%")  # для відлагодження

            if abs(imbalance) > 1:  # знижено до 1%
                side = "⬆ BUY" if imbalance > 0 else "⬇ SELL"
                msg = f"📊 DeepLocal Signal:
{side} imbalance: {imbalance}%"
                bot.send_message(chat_id=CHAT_ID, text=msg)
    except Exception as e:
        print("Error in analyze_orderbook:", e)

# WebSocket-підключення
async def start_websocket():
    url = "wss://stream.binance.com:9443/ws/ethusdt@depth20@100ms"
    async with websockets.connect(url) as ws:
        while True:
            message = await ws.recv()
            await analyze_orderbook(message)

# Запуск WebSocket у потоці
def run_ws():
    asyncio.new_event_loop().run_until_complete(start_websocket())

def start_ws_thread():
    global ws_started
    if not ws_started:
        threading.Thread(target=run_ws, daemon=True).start()
        ws_started = True

# Запуск Flask і WebSocket
if __name__ == "__main__":
    start_ws_thread()
    app.run(host="0.0.0.0", port=8080)