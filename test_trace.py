import requests
import json

BASE_URL = "http://127.0.0.1:5000"

def test_trace():
    print("Testing Trace...")
    # Ensure dataset is loaded
    requests.post(f"{BASE_URL}/api/dataset", json={"name": "sample_dna"})
    
    payload = {
        "algorithm": "Finite Automata",
        "pattern": "GATC"
    }
    response = requests.post(f"{BASE_URL}/api/trace", json=payload)
    
    if response.status_code == 200:
        data = response.json()
        if "steps" in data and len(data["steps"]) > 0:
            print(f"PASS: Trace returned {len(data['steps'])} steps")
            # Check first step structure
            print("First step:", data["steps"][0])
        else:
            print(f"FAIL: No steps returned. Data: {data}")
    else:
        print(f"FAIL: Status code {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    try:
        test_trace()
    except Exception as e:
        print(f"ERROR: {e}")
