import requests
import json

BASE_URL = "http://localhost:8000/api"

def test_api():
    try:
        print(f"Checking {BASE_URL}/symbols...")
        res = requests.get(f"{BASE_URL}/symbols")
        print(f"Status: {res.status_code}")
        if res.status_code == 200:
            symbols = res.json()
            print(f"Total symbols: {len(symbols)}")
            if symbols:
                print(f"First 10 symbols: {symbols[:10]}")
            else:
                print("SYMBOL LIST IS EMPTY!")
        else:
            print(f"Error: {res.text}")
            
        print(f"\nChecking {BASE_URL}/status...")
        res = requests.get(f"{BASE_URL}/status")
        print(f"Status: {res.json()}")
        
    except Exception as e:
        print(f"FAILED: {e}")

if __name__ == "__main__":
    test_api()
