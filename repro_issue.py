from src.algorithims.finite_automata import FiniteAutomataMatching

def test_fa():
    print("--- Test 1: Case Insensitive (simulated) ---")
    text = "*** start ... [illustration] ...".lower()
    pattern = "st"
    print(f"Text: {text}")
    print(f"Pattern: {pattern}")
    
    fa = FiniteAutomataMatching(pattern)
    matches = fa.search(text)
    print(f"Matches: {matches}")
    
    # Check if 'illustration' (index ~15) is found
    # illustration starts at index 15 in the string above
    # st is at index 20
    
    print("\n--- Test 2: Case Sensitive ---")
    text = "*** START ... [Illustration] ..."
    pattern = "ST"
    print(f"Text: {text}")
    print(f"Pattern: {pattern}")
    
    fa = FiniteAutomataMatching(pattern)
    matches = fa.search(text)
    print(f"Matches: {matches}")

if __name__ == "__main__":
    test_fa()
