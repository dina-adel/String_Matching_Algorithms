from src.algorithims.finite_automata import FiniteAutomataMatching
from src.algorithims.z import ZAlgorithm
from src.algorithims.bitap import BitapAlgorithm
from src.performance_evaluator import PerformanceEvaluator
from pathlib import Path

def main():
    """Example usage of enhanced evaluator."""

    evaluator = PerformanceEvaluator()
    
    algorithms = {
        "Finite Automata": FiniteAutomataMatching,
        "Z-Algorithm": ZAlgorithm,
        "Bitap": BitapAlgorithm
    }
    
    scales = [100_000, 500_000, 1_000_000, 5_000_000, 10_000_000]
    dataset_types = ["dna_random", "repetitive"]
    
    dataset_dir = Path("data/generated")
    
    for dtype in dataset_types:
        evaluator.benchmark_scale(algorithms, dataset_dir, dtype, scales)
    
    # Generate outputs
    evaluator.save_results()
    evaluator.generate_report()
    
    print("\n" + "="*70)
    print("BENCHMARKING COMPLETE")
    print("="*70)


if __name__ == "__main__":
    main()