import requests
import json

BASE_URL = "http://127.0.0.1:5000"

def test_compare_all():
    print("Testing Compare All...")
    payload = {
        "type": "search",
        "algorithm": "All",
        "pattern": "GATC"
    }
    response = requests.post(f"{BASE_URL}/api/operation", json=payload)
    if response.status_code == 200:
        data = response.json()
        if isinstance(data, list) and len(data) >= 2:
            print("PASS: Compare All returned list of results")
        else:
            print(f"FAIL: Expected list, got {type(data)}")
    else:
        print(f"FAIL: Status code {response.status_code}")

def test_export():
    print("Testing Export...")
    # Run an operation first to populate results
    test_compare_all()
    
    response = requests.get(f"{BASE_URL}/api/export")
    if response.status_code == 200:
        if "text/csv" in response.headers["Content-Type"]:
            print("PASS: Export returned CSV")
        else:
            print(f"FAIL: Content-Type {response.headers['Content-Type']}")
    else:
        print(f"FAIL: Export status {response.status_code}")

if __name__ == "__main__":
    try:
        test_compare_all()
        test_export()
    except Exception as e:
        print(f"ERROR: {e}")
