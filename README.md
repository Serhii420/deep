# DeepLocal Telegram Bot

## 🔧 Інструкція запуску на Render

1. Форкни або завантаж цей репозиторій у себе на GitHub.
2. Перейди на [https://render.com](https://render.com) > New Web Service.
3. Обери GitHub репозиторій.
4. Start command: `python main.py`
5. Build command: *(залиш пустим)*
6. Встанови Webhook:

```
https://api.telegram.org/bot<YOUR_TOKEN>/setWebhook?url=https://<your-render-url>/<YOUR_TOKEN>
```