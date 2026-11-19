import os, time, yfinance as yf, pandas as pd, requests
from datetime import datetime, timezone, timedelta

BOT_TOKEN = os.getenv("9266653853:AAFpf9kwzoyvspyGzl9tx_swERivkHXYB0Y")
CHAT_ID = os.getenv("@brightfx555")

# 30 REAL PAIRS FOR IQ OPTION REAL - WITH USD/PLN & USD/NGN
PAIRS = {
    "EUR/USD": "EURUSD=X",
    "GBP/USD": "GBPUSD=X",
    "USD/JPY": "USDJPY=X",
    "AUD/USD": "AUDUSD=X",
    "USD/CAD": "USDCAD=X",
    "USD/CHF": "USDCHF=X",
    "NZD/USD": "NZDUSD=X",
    "EUR/GBP": "EURGBP=X",
    "EUR/JPY": "EURJPY=X",
    "GBP/JPY": "GBPJPY=X",
    "AUD/JPY": "AUDJPY=X",
    "EUR/AUD": "EURAUD=X",
    "EUR/CAD": "EURCAD=X",
    "EUR/CHF": "EURCHF=X",
    "GBP/AUD": "GBPAUD=X",
    "GBP/CAD": "GBPCAD=X",
    "GBP/CHF": "GBPCHF=X",
    "AUD/CAD": "AUDCAD=X",
    "AUD/CHF": "AUDCHF=X",
    "AUD/NZD": "AUDNZD=X",
    "NZD/JPY": "NZDJPY=X",
    "NZD/CAD": "NZDCAD=X",
    "NZD/CHF": "NZDCHF=X",
    "CAD/JPY": "CADJPY=X",
    "CAD/CHF": "CADCHF=X",
    "CHF/JPY": "CHFJPY=X",
    "EUR/NZD": "EURNZD=X",
    "GBP/NZD": "GBPNZD=X",
    "USD/PLN": "USDPLN=X",
    "USD/NGN": "USDNGN=X",
}

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": CHAT_ID, "text": msg, "parse_mode": "HTML"})

def get_rsi(close, period=14):
    delta = close.diff()
    gain = delta.where(delta > 0, 0).rolling(period).mean()
    loss = -delta.where(delta < 0, 0).rolling(period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def check_pair(name, ticker):
    try:
        df = yf.download(ticker, period="1d", interval="5m", progress=False, auto_adjust=False)
        if len(df) < 30:
            return None
        df.columns = [c[0] if isinstance(c, tuple) else c for c in df.columns]
        close = df['Close']
        rsi = get_rsi(close).iloc[-1]
        ema9 = close.ewm(span=9).mean().iloc[-1]
        ema21 = close.ewm(span=21).mean().iloc[-1]
        price = close.iloc[-1]
        signal = None
        if rsi < 35 and ema9 > ema21 and price > ema21:
            signal = "BUY 🟢 CALL"
        elif rsi > 65 and ema9 < ema21 and price < ema21:
            signal = "SELL 🔴 PUT"
        if signal:
            now_wat = datetime.now(timezone.utc) + timedelta(hours=1)
            enter_time = now_wat + timedelta(minutes=2)
            return f"📊 <b>{name} - IQ OPTION REAL</b>\nSignal: <b>{signal}</b>\nPrice: {price:.5f}\nRSI: {rsi:.1f}\n🕐 ENTER AT: <b>{enter_time.strftime('%H:%M')} WAT</b>\n⏳ EXPIRY: <b>5 Minutes</b>"
        return None
    except Exception as e:
        print(f"Error {name}: {e}")
        return None

def main():
    print("IQ OPTION REAL BOT - 30 PAIRS STARTED")
    while True:
        signals = []
        for name, ticker in PAIRS.items():
            s = check_pair(name, ticker)
            if s:
                signals.append(s)
            time.sleep(2)  # Delay so Yahoo no block us
        if signals:
            msg = "🔥 <b>IQ OPTION REAL - 5M SIGNAL</b> 🔥\n\n" + "\n\n---\n\n".join(signals)
            send_telegram(msg)
        time.sleep(300)

if __name__ == "__main__":
    main()
