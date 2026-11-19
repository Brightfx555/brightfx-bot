import os
import time
import requests

TOKEN = os.getenv("9266653853:AAFpf9kwzoyvspyGzl9tx_swERivkHXYB0Y")
CHAT_ID = os.getenv("@brightfx555")

PAIRS = ["EURUSD=X", "GBPUSD=X", "USDJPY=X", "AUDUSD=X", "USDCAD=X", "USDCHF=X", "NZDUSD=X", "EURGBP=X", "EURJPY=X", "GBPJPY=X", "AUDJPY=X", "EURAUD=X", "EURNZD=X", "GBPAUD=X", "GBPCHF=X", "CADJPY=X", "CHFJPY=X", "EURCAD=X", "EURCHF=X", "AUDCAD=X", "AUDCHF=X", "NZDJPY=X", "NZDCAD=X", "NZDCHF=X", "GBPCAD=X", "GBPNZD=X", "EURSEK=X", "USDSEK=X", "USDMXN=X", "USDZAR=X"]

NAMES = {"EURUSD=X":"EUR/USD", "GBPUSD=X":"GBP/USD", "USDJPY=X":"USD/JPY", "AUDUSD=X":"AUD/USD", "USDCAD=X":"USD/CAD", "USDCHF=X":"USD/CHF", "NZDUSD=X":"NZD/USD", "EURGBP=X":"EUR/GBP", "EURJPY=X":"EUR/JPY", "GBPJPY=X":"GBP/JPY", "AUDJPY=X":"AUD/JPY", "EURAUD=X":"EUR/AUD", "EURNZD=X":"EUR/NZD", "GBPAUD=X":"GBP/AUD", "GBPCHF=X":"GBP/CHF", "CADJPY=X":"CAD/JPY", "CHFJPY=X":"CHF/JPY", "EURCAD=X":"EUR/CAD", "EURCHF=X":"EUR/CHF", "AUDCAD=X":"AUD/CAD", "AUDCHF=X":"AUD/CHF", "NZDJPY=X":"NZD/JPY", "NZDCAD=X":"NZD/CAD", "NZDCHF=X":"NZD/CHF", "GBPCAD=X":"GBP/CAD", "GBPNZD=X":"GBP/NZD", "EURSEK=X":"EUR/SEK", "USDSEK=X":"USD/SEK", "USDMXN=X":"USD/MXN", "USDZAR=X":"USD/ZAR"}

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"}, timeout=10)

def get_candles(symbol):
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?range=1d&interval=5m"
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(url, headers=headers, timeout=10).json()
    res = r["chart"]["result"][0]
    closes = res["indicators"]["quote"][0]["close"]
    return [c for c in closes if c is not None]

def rsi(closes, period=14):
    gains, losses = [], []
    for i in range(1, len(closes)):
        diff = closes[i] - closes[i-1]
        gains.append(max(diff, 0))
        losses.append(max(-diff, 0))
    if len(gains) < period:
        return 50
    avg_gain = sum(gains[-period:]) / period
    avg_loss = sum(losses[-period:]) / period
    if avg_loss == 0:
        return 100
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def ema(closes, period):
    k = 2 / (period + 1)
    e = closes[0]
    for c in closes[1:]:
        e = c * k + e * (1 - k)
    return e

def check():
    for sym in PAIRS:
        try:
            closes = get_candles(sym)
            if len(closes) < 20:
                continue
            last = closes[-1]
            r = rsi(closes)
            e9 = ema(closes, 9)
            e21 = ema(closes, 21)
            name = NAMES[sym]
            signal = None
            if r < 30 and last > e9:
                signal = "CALL 🟢 UP"
            elif r > 70 and last < e9:
                signal = "PUT 🔴 DOWN"
            if signal:
                msg = f"📊 *{name} SIGNAL*\n\nDirection: {signal}\nPrice: {last:.5f}\nRSI: {r:.1f}\nEMA9: {e9:.5f} | EMA21: {e21:.5f}\nTimeframe: 5M\n\n💰 *Martingale:*\nLevel 1: $1\nLevel 2: $2.20\nLevel 3: $4.80\n\n⚠️ Trade manually for IQ Option. No auto-trade."
                send_telegram(msg)
                print(f"Sent {name} {signal}")
            else:
                print(f"{name} no signal RSI {r:.1f}")
        except Exception as e:
            print(f"Error {sym}: {e}")
        time.sleep(1)

send_telegram("✅ Safe Bot Started — 30 Pairs, No IQ Login, signals only. I go check every 5 mins.")
while True:
    check()
    time.sleep(300)
