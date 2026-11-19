import os
import time
import threading
import requests
import yfinance as yf
import pandas as pd
import numpy as np
from flask import Flask

app = Flask(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Loosened small so signals go come more
RSI_BUY = 35
RSI_SELL = 65
CHECK_EVERY = 300  # 5 mins

PAIRS = [
    "EURUSD=X", "GBPUSD=X", "USDJPY=X", "AUDUSD=X", "USDCAD=X",
    "EURGBP=X", "EURJPY=X", "GBPJPY=X", "AUDJPY=X", "NZDUSD=X",
    "USDCHF=X", "EURCHF=X", "GBPCHF=X", "AUDCAD=X", "AUDCHF=X",
    "CADJPY=X", "CHFJPY=X", "EURAUD=X", "EURCAD=X", "GBPAUD=X",
    "GBPCAD=X", "NZDJPY=X", "NZDCAD=X", "NZDCHF=X", "AUDNZD=X",
    "CADCHF=X", "EURNZD=X", "GBPNZD=X", "USDTRY=X", "EURTRY=X"
]

def send_telegram(msg):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("No Telegram config", flush=True)
        return
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(url, json={"chat_id": TELEGRAM_CHAT_ID, "text": msg, "parse_mode": "HTML"}, timeout=10)
        print(f"Sent Telegram: {msg[:50]}", flush=True)
    except Exception as e:
        print(f"Telegram error: {e}", flush=True)

def calc_rsi(data, period=14):
    delta = data.diff()
    gain = delta.where(delta > 0, 0).rolling(window=period).mean()
    loss = -delta.where(delta < 0, 0).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def check_one_pair(ticker):
    try:
        df = yf.download(ticker, period="1d", interval="5m", progress=False)
        if df.empty or len(df) < 20:
            return None
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        close = df['Close']
        rsi = calc_rsi(close).iloc[-1]
        ema20 = close.ewm(span=20).mean().iloc[-1]
        price = float(close.iloc[-1])
        name = ticker.replace("=X", "")
        print(f"{name}: Price={price:.5f} RSI={rsi:.1f} EMA20={ema20:.5f}", flush=True)
        if rsi <= RSI_BUY and price > ema20:
            return f"🟢 <b>BUY {name}</b>\nPrice: {price:.5f}\nRSI: {rsi:.1f} | EMA20: {ema20:.5f}\nTime: 5M | Expiry: 5 mins"
        if rsi >= RSI_SELL and price < ema20:
            return f"🔴 <b>SELL {name}</b>\nPrice: {price:.5f}\nRSI: {rsi:.1f} | EMA20: {ema20:.5f}\nTime: 5M | Expiry: 5 mins"
        return None
    except Exception as e:
        print(f"Error {ticker}: {e}", flush=True)
        return None

def bot_loop():
    print("Bot loop started...", flush=True)
    send_telegram("✅ <b>Safe Bot Started - FIXED VERSION</b>\n30 Pairs, I go check every 5 mins and I go write for logs.")
    while True:
        try:
            print(f"--- Checking... {time.strftime('%H:%M:%S')} ---", flush=True)
            found = 0
            for ticker in PAIRS:
                signal = check_one_pair(ticker)
                if signal:
                    send_telegram(f"📈 <b>BRIGHT FX SIGNAL</b>\n\n{signal}\n\n⚠️ Trade with care, no 95% guarantee.")
                    found += 1
                    time.sleep(2)
            if found == 0:
                print("No signal this round, waiting 5 mins...", flush=True)
            time.sleep(CHECK_EVERY)
        except Exception as e:
            print(f"Loop error: {e}", flush=True)
            time.sleep(60)

@app.route('/')
def home():
    return "Bot is running!"

# Start loop in background so Flask + Bot go run together
threading.Thread(target=bot_loop, daemon=True).start()

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
