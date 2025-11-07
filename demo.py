from src.performance_evaluator import PerformanceEvaluator
from src.datasets.sample_dataset import load_sample_dataset
from src.algorithims.finite_automata import FiniteAutomataMatching
from src.algorithims.z import ZAlgorithm    
from src.algorithims.bitap import BitapAlgorithm

def main():
    """
    Main function to run demonstrations and performance tests.
    """
    print("=" * 70)
    print("STRING MATCHING ALGORITHMS - DEMONSTRATION")
    print("=" * 70)
    
    # Load dataset
    dataset = load_sample_dataset()
    
    # Test on DNA sequences
    print("\n1. DNA SEQUENCE MATCHING")
    print("-" * 70)
    dna_text = dataset['dna']['text']
    print(f"Text length: {len(dna_text)} characters")
    
    all_results = []
    test_labels = []
    
    for pattern in dataset['dna']['patterns']:
        print(f"\nSearching for pattern: '{pattern}'")
        results = PerformanceEvaluator.run_comparison(dna_text, pattern)
        all_results.append(results)
        test_labels.append(f"DNA-{pattern}")
        
        for algo_name, data in results.items():
            print(f"  {algo_name:20s}: Found {data['count']:3d} matches in {data['time']*1000:.4f} ms")
    
    # Test on book text
    print("\n\n2. BOOK TEXT MATCHING")
    print("-" * 70)
    book_text = dataset['book']['text']
    print(f"Text length: {len(book_text)} characters")
    
    for pattern in dataset['book']['patterns']:
        print(f"\nSearching for pattern: '{pattern}'")
        results = PerformanceEvaluator.run_comparison(book_text, pattern)
        all_results.append(results)
        test_labels.append(f"Text-{pattern[:10]}")
        
        for algo_name, data in results.items():
            print(f"  {algo_name:20s}: Found {data['count']:3d} matches in {data['time']*1000:.4f} ms")
    
    # Plot results
    print("\n\n3. GENERATING PERFORMANCE PLOTS")
    print("-" * 70)
    PerformanceEvaluator.plot_results(all_results, test_labels, 
                                     "String Matching Algorithms Performance Comparison")
    print("Plot saved as 'performance_comparison.png'")
    
    # Verification test
    print("\n\n4. CORRECTNESS VERIFICATION")
    print("-" * 70)
    test_text = "AABAACAADAABAABA"
    test_pattern = "AABA"
    print(f"Text: {test_text}")
    print(f"Pattern: {test_pattern}")
    
    fa = FiniteAutomataMatching(test_pattern)
    z = ZAlgorithm(test_pattern)
    bitap = BitapAlgorithm(test_pattern)
    
    matches_fa = fa.search(test_text)
    matches_z = z.search(test_text)
    matches_bitap = bitap.search(test_text)
    
    print(f"FA matches:     {matches_fa}")
    print(f"Z-Algo matches: {matches_z}")
    print(f"Bitap matches:  {matches_bitap}")
    print(f"All algorithms agree: {matches_fa == matches_z == matches_bitap}")
    
    print("\n" + "=" * 70)
    print("DEMONSTRATION COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()