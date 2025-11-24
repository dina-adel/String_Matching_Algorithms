import time
import tracemalloc
from typing import Dict, List, Tuple, Any

# Import existing algorithms
from src.algorithims.finite_automata import FiniteAutomataMatching
from src.algorithims.z import ZAlgorithm
from src.algorithims.bitap import BitapAlgorithm

class AlgorithmWrapper:
    """
    Wrapper class to standardize operations (Search, Insert, Delete) 
    across different string matching algorithms and measure performance.
    """

    @staticmethod
    def _get_algorithm_instance(algo_name: str, pattern: str):
        if algo_name == "Finite Automata":
            return FiniteAutomataMatching(pattern)
        elif algo_name == "Z-Algorithm":
            return ZAlgorithm(pattern)
        elif algo_name == "Bitap":
            if len(pattern) > 64:
                raise ValueError("Bitap algorithm only supports patterns up to 64 characters.")
            return BitapAlgorithm(pattern)
        else:
            raise ValueError(f"Unknown algorithm: {algo_name}")

    @staticmethod
    def run_operation(operation_type: str, algo_name: str, text: str, pattern: str, insert_text: str = "") -> Dict[str, Any]:
        """
        Executes the specified operation and returns the result along with performance metrics.
        """
        
        # Start measuring resources
        tracemalloc.start()
        start_time = time.perf_counter()
        
        result = {}
        matches = []
        updated_text = text
        
        try:
            algorithm = AlgorithmWrapper._get_algorithm_instance(algo_name, pattern)
            
            # 1. Search Operation (Common to all)
            matches = algorithm.search(text)
            
            if operation_type == "search":
                pass 
                
            elif operation_type == "delete":
                sorted_matches = sorted(matches, reverse=True)
                pattern_len = len(pattern)
                current_text = text
                for start_idx in sorted_matches:
                    current_text = current_text[:start_idx] + current_text[start_idx + pattern_len:]
                updated_text = current_text
                
            elif operation_type == "insert":
                sorted_matches = sorted(matches, reverse=True)
                pattern_len = len(pattern)
                current_text = text
                for start_idx in sorted_matches:
                    insert_pos = start_idx + pattern_len
                    current_text = current_text[:insert_pos] + insert_text + current_text[insert_pos:]
                updated_text = current_text
                
            else:
                raise ValueError(f"Unknown operation: {operation_type}")
                
        except Exception as e:
            tracemalloc.stop()
            return {"error": str(e)}

        # Stop measuring
        end_time = time.perf_counter()
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        return {
            "matches": matches,
            "match_count": len(matches),
            "updated_text": updated_text,
            "time_taken": end_time - start_time,
            "space_peak": peak,
            "operation": operation_type,
            "algorithm": algo_name
        }

    @staticmethod
    def run_bulk_search(algo_name: str, text: str, patterns: List[str]) -> Dict[str, Any]:
        """
        Runs search for multiple patterns and aggregates results.
        """
        tracemalloc.start()
        start_time = time.perf_counter()
        
        total_matches = 0
        results_per_pattern = []
        
        try:
            for pattern in patterns:
                if not pattern.strip(): continue
                
                # Skip Bitap for long patterns
                if algo_name == "Bitap" and len(pattern) > 64:
                    results_per_pattern.append({"pattern": pattern, "count": 0, "error": "Pattern too long"})
                    continue

                algorithm = AlgorithmWrapper._get_algorithm_instance(algo_name, pattern)
                matches = algorithm.search(text)
                count = len(matches)
                total_matches += count
                results_per_pattern.append({"pattern": pattern, "count": count})
                
        except Exception as e:
            tracemalloc.stop()
            return {"error": str(e)}

        end_time = time.perf_counter()
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        return {
            "total_matches": total_matches,
            "pattern_count": len(patterns),
            "time_taken": end_time - start_time,
            "space_peak": peak,
            "details": results_per_pattern,
            "algorithm": algo_name
        }

    @staticmethod
    def run_trace(algo_name: str, text: str, pattern: str) -> Dict[str, Any]:
        """
        Generates a step-by-step trace of the algorithm for visualization.
        """
        steps = []
        n = len(text)
        m = len(pattern)
        
        if n > 100:
            return {"error": "Text too long for visualization (max 100 chars)"}

        if algo_name == "Finite Automata":
            # Use the actual class to get the transition table
            try:
                fa = FiniteAutomataMatching(pattern)
                transition_table = fa.transition_table
            except Exception as e:
                return {"error": f"Failed to initialize FA: {str(e)}"}

            state = 0
            for i in range(n):
                char = text[i]
                # Look up next state
                # The table keys are (state, char)
                # If char not in alphabet, it might not be in table, or FA handles it.
                # The FA implementation resets to 0 if char not in table (lines 111-115 of finite_automata.py)
                
                next_state = transition_table.get((state, char), 0)
                
                steps.append({
                    "index": i,
                    "state": state,
                    "char": char,
                    "match": False,
                    "description": f"State {state}, Read '{char}' -> State {next_state}"
                })
                
                state = next_state
                if state == m:
                    steps[-1]["match"] = True
                    steps[-1]["description"] += " -> MATCH!"

        elif algo_name == "Z-Algorithm":
            # Simulate Z-Algo comparison
            concat = pattern + "$" + text
            l = len(concat)
            # We only trace the part corresponding to 'text'
            # This is a simplified view showing the scan
            for i in range(m + 1, l):
                steps.append({
                    "index": i - (m + 1),
                    "char": concat[i],
                    "description": f"Scanning index {i - (m + 1)}"
                })
                if concat[i] == pattern[0]:
                     steps[-1]["possible_match"] = True

        elif algo_name == "Bitap":
             # Simulate Bitap
             steps.append({"description": "Bitap uses bitwise operations, scanning text..."})
             for i in range(n):
                 steps.append({
                     "index": i,
                     "char": text[i],
                     "description": f"Processing char '{text[i]}'"
                 })

        return {"steps": steps, "algorithm": algo_name}

    @staticmethod
    def generate_text(type: str, length: int) -> str:
        """
        Generates a random dataset of the specified type and length.
        """
        import random
        import string

        if length > 1000000:
            raise ValueError("Max length is 1,000,000 characters")

        if type == "dna":
            return ''.join(random.choices("ACGT", k=length))
        elif type == "text":
            # Use printable characters (letters, digits, punctuation, space)
            chars = string.ascii_letters + string.digits + " .,!?"
            return ''.join(random.choices(chars, k=length))
        else:
            raise ValueError("Unknown type")

    @staticmethod
    def run_benchmark(algo_name: str, pattern: str, max_length: int, step: int) -> Dict[str, Any]:
        """
        Runs a benchmark (Time vs Length) for the specified algorithm.
        """
        results = []
        
        # Generate a large text once (DNA for consistency)
        full_text = AlgorithmWrapper.generate_text("dna", max_length)
        
        for length in range(step, max_length + 1, step):
            text_slice = full_text[:length]
            
            # Run operation
            tracemalloc.start()
            start_time = time.perf_counter()
            
            try:
                algorithm = AlgorithmWrapper._get_algorithm_instance(algo_name, pattern)
                algorithm.search(text_slice)
            except Exception as e:
                tracemalloc.stop()
                return {"error": str(e)}
                
            end_time = time.perf_counter()
            current, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            
            results.append({
                "length": length,
                "time": end_time - start_time,
                "space": peak
            })
            
        return {"algorithm": algo_name, "data": results}
