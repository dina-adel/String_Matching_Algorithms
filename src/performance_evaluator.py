"""
Enhanced Performance Evaluator with Scaling Analysis
Tests algorithms across multiple scales and generates comprehensive reports
"""

import time
import json
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from typing import Dict, List, Tuple
from dataclasses import dataclass, asdict
import random
import tracemalloc
import sys

# Algorithm Imports
from src.algorithims.finite_automata import FiniteAutomataMatching
from src.algorithims.z import ZAlgorithm
from src.algorithims.bitap import BitapAlgorithm


# ============================================================================ #
#                              BENCHMARK RESULT                                #
# ============================================================================ #

@dataclass
class BenchmarkResult:
    """Store results from a single benchmark run."""
    algorithm: str
    dataset_type: str
    text_size: int
    pattern_length: int
    pattern: str
    matches_found: int

    # Mean values (main)
    time_ms: float
    preprocessing_time_ms: float
    search_time_ms: float

    # Memory metrics
    memory_peak_kb: float = 0.0
    memory_preprocessing_kb: float = 0.0
    memory_search_kb: float = 0.0

    # Statistical fields
    time_ms_std: float = 0.0
    time_ms_min: float = 0.0
    time_ms_max: float = 0.0
    memory_peak_kb_std: float = 0.0
    memory_peak_kb_min: float = 0.0
    memory_peak_kb_max: float = 0.0


# ============================================================================ #
#                          PERFORMANCE EVALUATOR                               #
# ============================================================================ #

class PerformanceEvaluator:
    """Enhanced evaluator with scaling analysis and detailed metrics."""

    def __init__(self, output_dir: str = "results", seed: int = 42):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.results: List[BenchmarkResult] = []

        # Seed for reproducibility
        self.seed = seed
        np.random.seed(seed)
        random.seed(seed)

    # ---------------------------------------------------------------------- #
    #                   Preprocessing + Search Timers                        #
    # ---------------------------------------------------------------------- #

    def measure_with_preprocessing(self, AlgorithmClass, pattern: str, text: str):
        """
        Measure preprocessing time and memory separately from search time and memory.
        
        Returns:
            (matches, preprocessing_time_ms, search_time_ms, total_time_ms,
             memory_peak_kb, memory_prep_kb, memory_search_kb)
        """
        # Start memory tracking
        tracemalloc.start()
        
        # Measure preprocessing
        start_prep = time.perf_counter()
        algorithm = AlgorithmClass(pattern)
        end_prep = time.perf_counter()
        preprocessing_time = (end_prep - start_prep) * 1000
        
        # Get memory after preprocessing
        current_prep, peak_prep = tracemalloc.get_traced_memory()
        memory_prep_kb = peak_prep / 1024
        
        # Reset peak for search phase
        tracemalloc.reset_peak()
        
        # Measure search
        start_search = time.perf_counter()
        matches = algorithm.search(text)
        end_search = time.perf_counter()
        search_time = (end_search - start_search) * 1000
        
        # Get memory after search
        current_search, peak_search = tracemalloc.get_traced_memory()
        memory_search_kb = peak_search / 1024
        
        # Get overall peak memory
        memory_peak_kb = max(memory_prep_kb, memory_search_kb)
        
        # Stop tracking
        tracemalloc.stop()
        
        total_time = preprocessing_time + search_time

        return matches, preprocessing_time, search_time, total_time, memory_peak_kb, memory_prep_kb, memory_search_kb

    # ---------------------------------------------------------------------- #
    #                        RUN 2× FOR ACCURACY                              #
    # ---------------------------------------------------------------------- #

    def benchmark_single(self, algorithm_name: str, AlgorithmClass,
                         dataset_type: str, text: str, pattern: str) -> BenchmarkResult:
        """Run each benchmark 2 times for faster evaluation."""

        run_times = []
        prep_times = []
        search_times = []
        match_counts = []
        memory_peaks = []
        memory_preps = []
        memory_searches = []

        for _ in range(2):
            matches, prep, search, total, mem_peak, mem_prep, mem_search = self.measure_with_preprocessing(
                AlgorithmClass, pattern, text
            )
            run_times.append(total)
            prep_times.append(prep)
            search_times.append(search)
            match_counts.append(len(matches))
            memory_peaks.append(mem_peak)
            memory_preps.append(mem_prep)
            memory_searches.append(mem_search)

        result = BenchmarkResult(
            algorithm=algorithm_name,
            dataset_type=dataset_type,
            text_size=len(text),
            pattern_length=len(pattern),
            pattern=pattern[:50],
            matches_found=int(np.mean(match_counts)),

            # Mean values
            time_ms=float(np.mean(run_times)),
            preprocessing_time_ms=float(np.mean(prep_times)),
            search_time_ms=float(np.mean(search_times)),

            # Memory metrics
            memory_peak_kb=float(np.mean(memory_peaks)),
            memory_preprocessing_kb=float(np.mean(memory_preps)),
            memory_search_kb=float(np.mean(memory_searches)),

            # Time stats
            time_ms_std=float(np.std(run_times)),
            time_ms_min=float(np.min(run_times)),
            time_ms_max=float(np.max(run_times)),
            
            # Memory stats
            memory_peak_kb_std=float(np.std(memory_peaks)),
            memory_peak_kb_min=float(np.min(memory_peaks)),
            memory_peak_kb_max=float(np.max(memory_peaks)),
        )

        self.results.append(result)
        return result

    # ---------------------------------------------------------------------- #
    #                        SCALE TESTING LOOP                               #
    # ---------------------------------------------------------------------- #

    def benchmark_scale(self, algorithm_classes: Dict, dataset_dir: Path,
                        dataset_type: str, scales: List[int]):

        print(f"\n{'='*70}")
        print(f"BENCHMARKING: {dataset_type}")
        print(f"{'='*70}")

        scales_mapping = {
            1_000: "1K",
            10_000: "10K",
            100_000: "100K",
            500_000: "500K",
            1_000_000: "1M",
            5_000_000: "5M",
            10_000_000: "10M",
            25_000_000: "25M"
        }

        for scale in scales:
            text_file = dataset_dir / dataset_type / f"text_{scales_mapping[scale]}.txt"
            patterns_file = dataset_dir / dataset_type / f"patterns_{scales_mapping[scale]}.txt"

            print("\nDataset file:", text_file)
            print("Patterns file:", patterns_file)

            if not text_file.exists():
                print(f"  ⚠️  Skipping {scale:,} - file not found")
                continue

            print(f"  Scale: {scale:,} characters")

            # Read text (safe replacement)
            text = text_file.read_text(encoding="utf-8", errors="replace").replace("�", " ")

            patterns = []
            with open(patterns_file, 'r', encoding="utf-8", errors="replace") as f:
                for line in f:
                    line = line.replace("�", " ")
                    if line.strip() and not line.startswith('#'):
                        pattern = line.split('\t')[0].strip()
                        if pattern:
                            # Unescape special characters
                            pattern = pattern.replace('\\t', '\t').replace('\\n', '\n').replace('\\r', '\r')
                            patterns.append(pattern)

            if len(patterns) < 3:
                print("  ⚠️ Not enough patterns.")
                continue

            # First 3 patterns
            test_patterns = patterns[:3]

            for pattern in test_patterns:
                print(f"\n    Pattern: '{pattern[:30]}...' "
                      f"(len={len(pattern)}, occurs={text.count(pattern)}x)")

                for algo_name, AlgorithmClass in algorithm_classes.items():

                    if algo_name == "Bitap" and len(pattern) > 64:
                        print(f"      {algo_name:20s}: SKIPPED (pattern > 64 chars)")
                        continue

                    try:
                        result = self.benchmark_single(
                            algo_name, AlgorithmClass, dataset_type, text, pattern
                        )

                        print(f"      {algo_name:20s}: "
                              f"{result.time_ms:8.4f} ms  "
                              f"(mem={result.memory_peak_kb:8.2f} KB)  "
                              f"std={result.time_ms_std:6.4f}")

                    except Exception as e:
                        print(f"      {algo_name:20s}: ERROR - {str(e)}")

    
    # ---------------------------------------------------------------------- #
    #                          SAVE RESULTS                                   #
    # ---------------------------------------------------------------------- #

    def save_results(self, filename: str = "benchmark_results.json"):
        output_file = self.output_dir / filename
        results_dict = [asdict(r) for r in self.results]
        with open(output_file, 'w') as f:
            json.dump(results_dict, f, indent=2)
        print(f"✓ Saved results to: {output_file}")

    # ---------------------------------------------------------------------- #
    #                             REPORT                                       #
    # ---------------------------------------------------------------------- #

    def generate_report(self):
        report_file = self.output_dir / "benchmark_report.txt"

        with open(report_file, 'w') as f:
            f.write("="*70 + "\n")
            f.write("STRING MATCHING ALGORITHMS - BENCHMARK REPORT\n")
            f.write("="*70 + "\n\n")

            algorithms = sorted(set(r.algorithm for r in self.results))
            dataset_types = sorted(set(r.dataset_type for r in self.results))

            f.write(f"Total benchmarks: {len(self.results)}\n")
            f.write(f"Algorithms: {', '.join(algorithms)}\n")
            f.write(f"Datasets: {', '.join(dataset_types)}\n\n")

            f.write("-"*70 + "\n")
            f.write("BEST PERFORMERS\n")
            f.write("-"*70 + "\n\n")

            for dtype in dataset_types:
                f.write(f"\n{dtype}:\n")
                dr = [r for r in self.results if r.dataset_type == dtype]
                sizes = sorted(set(r.text_size for r in dr))
                for size in sizes:
                    sr = [r for r in dr if r.text_size == size]
                    best = min(sr, key=lambda x: x.time_ms)
                    best_mem = min(sr, key=lambda x: x.memory_peak_kb)
                    f.write(f"  {size:>10,} chars:\n")
                    f.write(f"    Fastest: {best.algorithm:20s} {best.time_ms:8.4f} ms\n")
                    f.write(f"    Lowest Memory: {best_mem.algorithm:20s} {best_mem.memory_peak_kb:8.2f} KB\n")

            f.write("\n" + "-"*70 + "\n")
            f.write("MEMORY USAGE SUMMARY\n")
            f.write("-"*70 + "\n\n")

            for algo in algorithms:
                ar = [r for r in self.results if r.algorithm == algo]
                avg_mem = np.mean([r.memory_peak_kb for r in ar])
                max_mem = max([r.memory_peak_kb for r in ar])
                min_mem = min([r.memory_peak_kb for r in ar])
                f.write(f"{algo}:\n")
                f.write(f"  Average: {avg_mem:8.2f} KB\n")
                f.write(f"  Range: {min_mem:8.2f} - {max_mem:8.2f} KB\n\n")

        print(f"✓ Saved report: {report_file}")

    # ---------------------------------------------------------------------- #
    #                        STATIC METHODS FOR DEMO                          #
    # ---------------------------------------------------------------------- #

    @staticmethod
    def run_comparison(text: str, pattern: str) -> Dict[str, Dict]:
        """
        Run all algorithms on a single text/pattern pair and return results.
        Used by demo.py.
        """
        results = {}
        
        algorithms = {
            "Finite Automata": FiniteAutomataMatching,
            "Z-Algorithm": ZAlgorithm,
            "Bitap": BitapAlgorithm
        }
        
        for name, AlgoClass in algorithms.items():
            try:
                # Skip Bitap for long patterns
                if name == "Bitap" and len(pattern) > 64:
                    results[name] = {'count': -1, 'time': 0.0}
                    continue
                    
                start_time = time.perf_counter()
                algo = AlgoClass(pattern)
                matches = algo.search(text)
                end_time = time.perf_counter()
                
                results[name] = {
                    'count': len(matches),
                    'time': end_time - start_time
                }
            except Exception as e:
                print(f"Error running {name}: {e}")
                results[name] = {'count': -1, 'time': 0.0}
                
        return results