import requests
import json
import time

BASE_URL = "http://localhost:8000/api"

def test_funnel():
    print(f"Testing High Performance Funnel at {BASE_URL}...")
    
    payload = {
        "symbol": "XAUUSDm",
        "timeframe": "M1",
        "type": "mean_reversion",
        "paramRanges": {
            "period": {"min": 5, "max": 25, "step": 2},
            "std": {"min": 1.0, "max": 3.0, "step": 0.5},
            "stopLoss": {"min": 10, "max": 50, "step": 10},
            "takeProfit": {"min": 20, "max": 100, "step": 20}
        },
        "criteria": "sharpe"
    } # Small enough to test the funnel/grid logic
    
    start = time.time()
    try:
        res = requests.post(f"{BASE_URL}/optimize", json=payload)
        end = time.time()
        
        print(f"Status: {res.status_code}")
        print(f"Time Taken: {end - start:.2f}s")
        
        if res.status_code == 200:
            data = res.json()
            print(f"Search Space: {data.get('totalSearchSpace')}")
            print(f"Total Tested: {data.get('totalTested')}")
            if data.get('bestConfig'):
                print(f"Best Sharpe: {data['bestConfig']['metrics']['sharpeIS']}")
        else:
            print(f"Error: {res.text}")
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    test_funnel()
