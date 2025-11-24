import requests
import json

def test_trace_api():
    url = "http://127.0.0.1:5000/api/trace"
    
    # Set the text first (using the dataset API or just relying on default)
    # Let's upload the specific text the user mentioned to be sure
    text = "*** START OF THE PROJECT GUTENBERG EBOOK 11 *** [Illustration] Alice’s Adventures in Wonderland by L"
    
    # We can't easily set the text via API without uploading a file or using internal state if we could.
    # But we can use the 'custom' upload if we want, or just rely on what's there.
    # Let's try to upload it as a custom dataset first to be sure we are testing the right thing.
    
    upload_url = "http://127.0.0.1:5000/api/upload"
    files = {'file': ('test.txt', text)}
    try:
        requests.post(upload_url, files=files)
        print("Uploaded test text.")
    except Exception as e:
        print(f"Failed to upload text: {e}")
        return

    print("\n--- Test 1: Case Insensitive (case_sensitive=False) ---")
    payload = {
        "algorithm": "Finite Automata",
        "pattern": "ST",
        "case_sensitive": False
    }
    try:
        res = requests.post(url, json=payload)
        data = res.json()
        
        if "error" in data:
            print(f"Error: {data['error']}")
        else:
            print(f"Case Sensitive returned: {data.get('case_sensitive')}")
            matches = [s for s in data.get('steps', []) if s.get('match')]
            print(f"Matches found: {len(matches)}")
            for m in matches:
                print(f"  Match at index {m.get('match_index')}: {m.get('description')}")
            
            # We expect matches for "START" (index ~4) and "Illustration" (index ~40)
            
    except Exception as e:
        print(f"Request failed: {e}")

    print("\n--- Test 2: Case Sensitive (case_sensitive=True) ---")
    payload = {
        "algorithm": "Finite Automata",
        "pattern": "ST",
        "case_sensitive": True
    }
    try:
        res = requests.post(url, json=payload)
        data = res.json()
        
        if "error" in data:
            print(f"Error: {data['error']}")
        else:
            print(f"Case Sensitive returned: {data.get('case_sensitive')}")
            matches = [s for s in data.get('steps', []) if s.get('match')]
            print(f"Matches found: {len(matches)}")
            for m in matches:
                print(f"  Match at index {m.get('match_index')}: {m.get('description')}")
            
            # We expect match ONLY for "START"
            
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    test_trace_api()
