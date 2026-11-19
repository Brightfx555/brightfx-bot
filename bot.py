import os
import time
from iqoptionapi.stable_api import IQ_Option

EMAIL = os.getenv("IQ_EMAIL")
PASSWORD = os.getenv("IQ_PASSWORD")

PAIR = os.getenv("PAIR", "EURUSD")
AMOUNT = float(os.getenv("AMOUNT", "1"))
DURATION = int(os.getenv("DURATION", "1"))

print("Connecting to IQ Option...")
api = IQ_Option(EMAIL, PASSWORD)
check, reason = api.connect()
print("Connected:", check, reason)

if not check:
    print("Login failed:", reason)
    raise SystemExit(1)

api.change_balance("PRACTICE")
print("Balance:", api.get_balance())

while True:
    try:
        candles = api.get_candles(PAIR, 60, 3, time.time())
        if not candles or len(candles) < 2:
            print("No candles, waiting...")
            time.sleep(5)
            continue

        last = candles[-2]
        direction = "call" if last["close"] > last["open"] else "put"
        print(f"Last candle {PAIR}: open={last['open']} close={last['close']} -> {direction}")

        status, order_id = api.buy(AMOUNT, PAIR, direction, DURATION)
        print("Trade:", status, order_id)

        if status:
            result = api.check_win_v4(order_id)
            print("Result:", result)

        print("Waiting 60s for next trade...")
        time.sleep(60)

    except Exception as e:
        print("Error:", e)
        time.sleep(10)
