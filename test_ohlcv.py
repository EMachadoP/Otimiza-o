import requests

BASE_URL = "http://localhost:8000/api"

def test_ohlcv():
    symbol = "EURUSDm"
    tf = "H1"
    url = f"{BASE_URL}/ohlcv?symbol={symbol}&timeframe={tf}"
    try:
        print(f"Checking {url}...")
        res = requests.get(url)
        print(f"Status: {res.status_code}")
        if res.status_code == 200:
            data = res.json()
            print(f"Total bars: {len(data)}")
            if data:
                print(f"First bar: {data[0]}")
            else:
                print("OHLCV DATA IS EMPTY!")
        else:
            print(f"Error: {res.text}")
    except Exception as e:
        print(f"FAILED: {e}")

if __name__ == "__main__":
    test_ohlcv()
