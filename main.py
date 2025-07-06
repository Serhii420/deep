import asyncio
import json
import requests
import websockets
from flask import Flask, request
from waitress import serve
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# === CONFIG ===
BOT_TOKEN = "7640189770:AAH01Kw3SGSXVZL6bBVStw4MWpzrCpPchpo"
CHAT_ID = 402100936
WS_URL = "wss://fstream.binance.com/ws/ethusdt@depth20@100ms"
IMBALANCE_THRESHOLD = 1.01

# === FLASK ===
app = Flask(__name__)

# === TELEGRAM HANDLER ===
async def imbalance_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📡 Очікуємо сигнал з біржі...")

# === ANALYSIS ===
def analyze_orderbook(data):
    try:
        bids = data["bids"]
        asks = data["asks"]
        bid_vol = sum(float(b[1]) for b in bids[:5])
        ask_vol = sum(float(a[1]) for a in asks[:5])

        if bid_vol > ask_vol * IMBALANCE_THRESHOLD:
            return "BUY"
        elif ask_vol > bid_vol * IMBALANCE_THRESHOLD:
            return "SELL"
        else:
            return None
    except Exception as e:
        print("Error analyzing:", e)
        return None

def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": CHAT_ID, "text": text})

# === WEBSOCKET WATCHER ===
async def watch_orderbook():
    async with websockets.connect(WS_URL) as ws:
        while True:
            try:
                msg = await ws.recv()
                data = json.loads(msg)
                signal = analyze_orderbook(data)
                if signal:
                    message = (
                        "📊 DeepLocal Signal:\n"
                        f"Market: ETH/USDT\n"
                        f"Signal: {signal} ⚡️"
                    )
                    send_telegram_message(message)
                    await asyncio.sleep(10)
            except Exception as e:
                print("WebSocket error:", e)
                await asyncio.sleep(5)

# === TELEGRAM BOT START ===
async def start_bot():
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("imbalance", imbalance_command))
    await application.initialize()
    await application.start()
    await application.updater.start_polling()
    asyncio.create_task(watch_orderbook())

# === START ALL ===
@app.route("/", methods=["GET"])
def home():
    return "Bot is running"

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(start_bot())
    serve(app, host="0.0.0.0", port=8080)
