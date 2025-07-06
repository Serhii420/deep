from flask import Flask, request
import requests

app = Flask(__name__)

TOKEN = "YOUR_BOT_TOKEN"
CHAT_ID = "YOUR_CHAT_ID"

@app.route('/')
def home():
    return "DeepLocal bot is running"

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    data = request.get_json()
    if "message" in data and "text" in data["message"]:
        text = data["message"]["text"]
        if text == "/imbalance":
            # Тут буде логіка імбалансу
            requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", json={
                "chat_id": CHAT_ID,
                "text": "Imbalance: Buy: 1.62 / Sell: 0.65"
            })
    return "OK", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)