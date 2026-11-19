import requests
import time
import threading
import os
from flask import Flask

# --- KEEP YOUR OWN TOKEN AND CHAT ID HERE ---
BOT_TOKEN = "9266653853:AAFpf9kwzoyvspyGzl9tx_swERivkHXYB0Y"
CHAT_ID = "@brightfx555"
# -------------------------------------------

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running"

def send_telegram(msg):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg}, timeout=10)
    except Exception as e:
        print(f"Telegram error: {e}")

# 30 pairs
PAIRS = [
    "EURUSD","GBPUSD","USDJPY","AUDUSD","USDCAD","USDCHF","NZDUSD",
    "EURGBP","EURJPY","GBPJPY","AUDJPY","CADJPY","CHFJPY","NZDJPY",
    "EURAUD","EURCAD","EURNZD","GBPAUD","GBPCAD","GBPNZD","AUDCAD",
    "AUDNZD","CADCHF","AUDCHF","NZDCHF","EURCHF","GBPCHF",
    "EURTRY","USDTRY","GBPTRY"
]

def get_rsi(symbol):
    try:
        # Use Binance klines for forex-like calc via Yahoo? We use TwelveData-style simple fetch
        # Using Binance for crypto-like pairs, fallback to Yahoo for forex
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}=X?range=5d&interval=5m"
        # Convert EURUSD -> EURUSD=X
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(url, headers=headers, timeout=10)
        data = r.json()
        closes = data['chart']['result'][0]['indicators']['quote'][0]['close']
        closes = [c for c in closes if c is not None]
        if len(closes) < 15:
            return None, None
        # RSI 14
        gains = []
        losses = []
        for i in range(1, 15):
            diff = closes[-15+i] - closes[-15+i-1]
            if diff > 0:
                gains.append(diff)
                losses.append(0)
            else:
                gains.append(0)
                losses.append(abs(diff))
        avg_gain = sum(gains)/14
        avg_loss = sum(losses)/14
        if avg_loss == 0:
            rsi = 100
        else:
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
        return closes[-1], round(rsi, 1)
    except Exception as e:
        print(f"{symbol} error: {e}")
        return None, None

def bot_loop():
    print("Bot loop started - NO EMA VERSION...")
    send_telegram("✅ Safe Bot Started - NO EMA, RSI ONLY\n30 Pairs, 5 Min Check")
    while True:
        try:
            print(f"\n--- Checking... {time.strftime('%H:%M:%S')} ---")
            found = 0
            for pair in PAIRS:
                price, rsi = get_rsi(pair)
                if price is None:
                    print(f"{pair}: No data")
                    continue
                print(f"{pair}: Price={round(price,4)} RSI={rsi}")
                signal = None
                if rsi >= 70:
                    signal = "SELL 🔴"
                elif rsi <= 30:
                    signal = "BUY 🟢"
                if signal:
                    found += 1
                    msg = f"📊 {pair} - {signal}\nPrice: {round(price,4)}\nRSI: {rsi}\nTimeframe: 5m\nExpiry: 5 mins"
                    send_telegram(msg)
                    print(f">>> SIGNAL SENT: {pair} {signal}")
            if found == 0:
                print("No signal this round, waiting 5 mins...")
            time.sleep(300)  # 5 mins
        except Exception as e:
            print(f"Loop error: {e}")
            time.sleep(30)

threading.Thread(target=bot_loop, daemon=True).start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
