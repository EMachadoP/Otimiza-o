import requests

endpoints = [
    "/",
    "/api/status",
    "/api/symbols",
    "/api/ohlcv?symbol=EURUSD&timeframe=H1",
    "/api/analysis?symbol=EURUSD&timeframe=H1",
    "/api/strategies?symbol=EURUSD&timeframe=H1",
    "/api/heatmap?symbol=EURUSD&timeframe=H1",
    "/api/ml-insights?symbol=EURUSD&timeframe=H1",
]

base_url = "http://127.0.0.1:8000"

print(f"Testing backend at {base_url}...")
for endpoint in endpoints:
    url = f"{base_url}{endpoint}"
    try:
        response = requests.get(url, timeout=2)
        print(f"GET {endpoint}: {response.status_code}")
        if response.status_code != 200:
            print(f"  Response: {response.text[:100]}")
    except Exception as e:
        print(f"GET {endpoint}: FAILED ({e})")

# Test POST endpoints with minimal payload
post_endpoints = [
    ("/api/convert-mql", {"code": "// Test"}),
    ("/api/export-ea", {"strategy": {"name": "Test", "parameters": {}, "indicators": [], "type": "trend"}}),
]

for endpoint, payload in post_endpoints:
    url = f"{base_url}{endpoint}"
    try:
        response = requests.post(url, json=payload, timeout=2)
        print(f"POST {endpoint}: {response.status_code}")
        if response.status_code != 200:
            print(f"  Response: {response.text[:100]}")
    except Exception as e:
        print(f"POST {endpoint}: FAILED ({e})")
