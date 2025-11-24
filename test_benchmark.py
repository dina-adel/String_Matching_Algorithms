import requests
import json
import time

BASE_URL = "http://127.0.0.1:5000"

def test_generate():
    print("Testing Generation...")
    payload = {
        "type": "dna",
        "length": 5000
    }
    response = requests.post(f"{BASE_URL}/api/generate", json=payload)
    if response.status_code == 200:
        data = response.json()
        if data.get("success") and len(data.get("text")) == 5000:
            print("PASS: Generated DNA of length 5000")
        else:
            print(f"FAIL: Generation response invalid: {data}")
    else:
        print(f"FAIL: Status code {response.status_code}")

def test_benchmark():
    print("Testing Benchmark...")
    payload = {
        "algorithm": "Finite Automata",
        "pattern": "GATC",
        "max_length": 5000,
        "step": 1000
    }
    response = requests.post(f"{BASE_URL}/api/benchmark", json=payload)
    if response.status_code == 200:
        data = response.json()
        if isinstance(data, list) and len(data) > 0:
            points = data[0].get("data", [])
            if len(points) >= 5:
                print(f"PASS: Benchmark returned {len(points)} data points")
            else:
                print(f"FAIL: Expected 5+ points, got {len(points)}")
        else:
            print(f"FAIL: Invalid benchmark response: {data}")
    else:
        print(f"FAIL: Status code {response.status_code}")

if __name__ == "__main__":
    # Wait for server to start
    time.sleep(2)
    try:
        test_generate()
        test_benchmark()
    except Exception as e:
        print(f"ERROR: {e}")
