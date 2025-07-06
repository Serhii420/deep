from flask import Flask, request
import requests

app = Flask(__name__)
TOKEN = "7640189770:AAH01Kw3SGSXVZL6bBVStw4MWpzrCpPchpo"
CHAT_ID = "402100936"

@app.route('/')
def home():
    return "DeepLocal bot running!"

@app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    data = request.get_json()

    if 'message' in data and 'text' in data['message']:
        text = data['message']['text']
        chat_id = data['message']['chat']['id']

        if text == "/imbalance":
            requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", json={
                "chat_id": chat_id,
                "text": "DeepLocal: очікуємо сигнал з біржі..."
            })

    return {'ok': True}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
