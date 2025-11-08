import time
from typing import List, Dict, Tuple
import matplotlib.pyplot as plt
import numpy as np
from src.algorithims.finite_automata import FiniteAutomataMatching
from src.algorithims.z import ZAlgorithm
from src.algorithims.bitap import BitapAlgorithm

class PerformanceEvaluator:
    """
    Evaluate and compare performance of string matching algorithms.
    """
    
    @staticmethod
    def measure_time(algorithm, text: str, pattern: str) -> Tuple[List[int], float]:
        """
        Measure execution time of an algorithm.
        
        Input:
            algorithm: Instance of matching algorithm
            text (str): Text to search in
            pattern (str): Pattern to search for
        Output:
            Tuple[List[int], float]: (matches found, execution time in seconds)
        """
        start_time = time.perf_counter()
        matches = algorithm.search(text)
        end_time = time.perf_counter()
        return matches, (end_time - start_time)
    
    @staticmethod
    def run_comparison(text: str, pattern: str) -> Dict[str, Dict]:
        """
        Run all algorithms and compare performance.
        
        Input:
            text (str): Text to search in
            pattern (str): Pattern to search for
        Output:
            Dict[str, Dict]: Results for each algorithm including matches and time
        """
        results = {}
        
        # Finite Automata
        print("\nRunning Finite Automata Matching...")
        fa = FiniteAutomataMatching(pattern)
        matches_fa, time_fa = PerformanceEvaluator.measure_time(fa, text, pattern)
        results['Finite Automata'] = {
            'matches': matches_fa,
            'time': time_fa,
            'count': len(matches_fa)
        }
        
        # Z-Algorithm
        print("Running Z-Algorithm Matching...")
        z_algo = ZAlgorithm(pattern)
        matches_z, time_z = PerformanceEvaluator.measure_time(z_algo, text, pattern)
        results['Z-Algorithm'] = {
            'matches': matches_z,
            'time': time_z,
            'count': len(matches_z)
        }
        
        # Bitap Algorithm (only if pattern length <= 64)
        print("Running Bitap Matching...")
        if len(pattern) <= 64:
            bitap = BitapAlgorithm(pattern)
            matches_bitap, time_bitap = PerformanceEvaluator.measure_time(bitap, text, pattern)
            results['Bitap'] = {
                'matches': matches_bitap,
                'time': time_bitap,
                'count': len(matches_bitap)
            }
        
        print("All algorithms completed.")
        print("-" * 40)
        return results
    
    @staticmethod
    def plot_results(results_list: List[Dict], labels: List[str], title: str = "Performance Comparison"):
        """
        Plot performance comparison results.
        
        Input:
            results_list (List[Dict]): List of result dictionaries from multiple runs
            labels (List[str]): Labels for each test case
            title (str): Plot title
        Output:
            None (displays plot)
        """
        algorithms = list(results_list[0].keys())
        x = np.arange(len(labels))
        width = 0.25
        
        fig, ax = plt.subplots(figsize=(8, 5))
        
        for i, algo in enumerate(algorithms):
            times = [results[algo]['time'] * 1000 for results in results_list]  # Convert to ms
            ax.bar(x + i * width, times, width, label=algo)
        
        ax.set_xlabel('Test Case')
        ax.set_ylabel('Time (milliseconds)')
        ax.set_title(title)
        ax.set_xticks(x + width)
        ax.set_xticklabels(labels, rotation=45, ha='right')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('performance_comparison.png', dpi=300, bbox_inches='tight')
        plt.show()