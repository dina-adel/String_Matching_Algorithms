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
                if not pattern.strip(): 
                    continue
                
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
        Shows how each algorithm actually works with the data.
        Note: Text should be pre-limited to 500 chars by the caller.
        """
        steps = []
        n = len(text)
        m = len(pattern)
        
        if m == 0:
            return {"error": "Pattern cannot be empty"}
        
        if n == 0:
            return {"error": "Text cannot be empty"}

        if algo_name == "Finite Automata":
            try:
                fa = FiniteAutomataMatching(pattern)
                transition_table = fa.transition_table
            except Exception as e:
                return {"error": f"Failed to initialize FA: {str(e)}"}

            # Step 0: Show the pattern and initial state
            steps.append({
                "type": "init",
                "pattern": pattern,
                "description": f"🔍 Finite Automata initialized for pattern: '{pattern}' (length {m})",
                "highlight_ranges": [],
                "state_info": f"Starting in state 0"
            })

            state = 0
            for i in range(n):
                char = text[i]
                prev_state = state
                next_state = transition_table.get((state, char), 0)
                
                # Highlight current position being checked
                step = {
                    "type": "compare",
                    "index": i,
                    "char": char,
                    "state": prev_state,
                    "next_state": next_state,
                    "match": False,
                    "description": f"📍 Position {i}: Read '{char}' | State {prev_state} → {next_state}",
                    "highlight_ranges": [{"start": i, "end": i + 1, "type": "current"}],
                    "state_info": f"State: {prev_state} → {next_state}"
                }
                
                state = next_state
                
                # Check if we found a match
                if state == m:
                    match_start = i - m + 1
                    step["match"] = True
                    step["match_index"] = match_start
                    step["description"] = f"✅ Position {i}: Read '{char}' → State {m} (MATCH at index {match_start}!)"
                    step["highlight_ranges"] = [
                        {"start": match_start, "end": i + 1, "type": "match"}
                    ]
                    step["state_info"] = f"MATCH FOUND! Pattern found at position {match_start}"
                
                steps.append(step)

        elif algo_name == "Z-Algorithm":
            # Build the concatenated string
            concat = pattern + "$" + text
            concat_len = len(concat)
            
            # Step 0: Show pattern and separator
            steps.append({
                "type": "init",
                "pattern": pattern,
                "description": f"🔍 Z-Algorithm: Pattern '{pattern}' concatenated with '$' separator",
                "highlight_ranges": [],
                "state_info": f"Looking for Z-values equal to pattern length ({m})"
            })
            
            # Calculate Z-array with visualization
            Z = [0] * concat_len
            Z[0] = concat_len
            
            L, R = 0, 0
            matches_found = []
            
            for i in range(1, concat_len):
                # Only visualize the text part (after pattern + $)
                if i <= m:
                    continue
                    
                text_idx = i - (m + 1)
                if text_idx >= n:
                    break
                
                # Calculate Z[i]
                if i > R:
                    # Case 1: Outside Z-box
                    L, R = i, i
                    while R < concat_len and concat[R] == concat[R - L]:
                        R += 1
                    Z[i] = R - L
                    R -= 1
                    
                    compare_len = Z[i]
                    step = {
                        "type": "compare",
                        "index": text_idx,
                        "z_value": Z[i],
                        "box": [L - (m + 1), max(0, R - (m + 1))],
                        "match": Z[i] == m,
                        "description": f"📍 Position {text_idx}: Outside Z-box, comparing prefix... Z = {Z[i]}",
                        "highlight_ranges": [
                            {"start": text_idx, "end": min(text_idx + compare_len, n), "type": "compare"}
                        ],
                        "state_info": f"Z-box: [{L - (m + 1)}, {R - (m + 1)}]"
                    }
                    
                    if Z[i] == m:
                        step["match_index"] = text_idx
                        step["description"] = f"✅ Position {text_idx}: Z = {m} → MATCH FOUND!"
                        step["highlight_ranges"] = [
                            {"start": text_idx, "end": text_idx + m, "type": "match"}
                        ]
                        step["state_info"] = f"MATCH! Z-value equals pattern length"
                        matches_found.append(text_idx)
                else:
                    # Case 2: Inside Z-box
                    k = i - L
                    if Z[k] < R - i + 1:
                        Z[i] = Z[k]
                    else:
                        L = i
                        while R < concat_len and concat[R] == concat[R - L]:
                            R += 1
                        Z[i] = R - L
                        R -= 1
                    
                    compare_len = Z[i]
                    step = {
                        "type": "compare",
                        "index": text_idx,
                        "z_value": Z[i],
                        "box": [L - (m + 1), max(0, R - (m + 1))],
                        "match": Z[i] == m,
                        "description": f"📍 Position {text_idx}: Inside Z-box, Z = {Z[i]}",
                        "highlight_ranges": [
                            {"start": text_idx, "end": min(text_idx + compare_len, n), "type": "compare"}
                        ],
                        "state_info": f"Using Z-box optimization"
                    }
                    
                    if Z[i] == m:
                        step["match_index"] = text_idx
                        step["description"] = f"✅ Position {text_idx}: Z = {m} → MATCH FOUND!"
                        step["highlight_ranges"] = [
                            {"start": text_idx, "end": text_idx + m, "type": "match"}
                        ]
                        step["state_info"] = f"MATCH! Z-value equals pattern length"
                        matches_found.append(text_idx)
                
                steps.append(step)

        elif algo_name == "Bitap":
            # Step 0: Initialize
            steps.append({
                "type": "init",
                "pattern": pattern,
                "description": f"🔍 Bitap Algorithm: Pattern '{pattern}' (bitwise matching)",
                "highlight_ranges": [],
                "state_info": f"Using bit vector of length {m}"
            })
            
            # Precompute pattern masks
            pattern_mask = {}
            for j, char in enumerate(pattern):
                if char not in pattern_mask:
                    pattern_mask[char] = 0
                pattern_mask[char] |= (1 << j)
            
            # Show mask info
            mask_desc = " | ".join([f"'{c}': {bin(pattern_mask[c])[2:].zfill(m)}" for c in sorted(pattern_mask.keys())[:5]])
            steps.append({
                "type": "setup",
                "description": f"📋 Pattern masks computed: {mask_desc}",
                "highlight_ranges": [],
                "state_info": "Bit masks ready for matching"
            })
            
            R = 0
            for i in range(n):
                char = text[i]
                old_R = R
                
                # Shift and add the character mask
                R = ((R << 1) | 1) & pattern_mask.get(char, 0)
                
                # Check if we have a match
                match = (R & (1 << (m - 1))) != 0
                
                step = {
                    "type": "compare",
                    "index": i,
                    "char": char,
                    "bit_vector": bin(R)[2:].zfill(m) if R > 0 else "0" * m,
                    "match": match,
                    "description": f"📍 Position {i}: Read '{char}' | Bit vector: {bin(R)[2:].zfill(m) if R > 0 else '0' * m}",
                    "highlight_ranges": [
                        {"start": i, "end": i + 1, "type": "current"}
                    ],
                    "state_info": f"Active bits: {bin(R).count('1')}"
                }
                
                if match:
                    match_start = i - m + 1
                    step["match_index"] = match_start
                    step["description"] = f"✅ Position {i}: Read '{char}' → MATCH at index {match_start}!"
                    step["highlight_ranges"] = [
                        {"start": match_start, "end": i + 1, "type": "match"}
                    ]
                    step["state_info"] = f"MATCH FOUND! MSB is set"
                
                steps.append(step)

        return {
            "steps": steps,
            "algorithm": algo_name,
            "pattern": pattern,
            "text": text,
            "pattern_length": m,
            "text_length": n
        }

    @staticmethod
    def generate_text(type: str, length: int) -> str:
        """
        Generates a random dataset of the specified type and length.
        """
        import random
        import string
        import urllib.request

        if length > 1000000:
            raise ValueError("Max length is 1,000,000 characters")

        if type == "dna":
            return ''.join(random.choices("ACGT", k=length))
        elif type == "text":
            # Try to fetch real English text from Project Gutenberg (Alice in Wonderland)
            try:
                url = "https://www.gutenberg.org/files/11/11-0.txt"
                with urllib.request.urlopen(url, timeout=5) as response:
                    data = response.read().decode('utf-8')
                
                # Clean up the text (remove header/footer roughly)
                start_idx = data.find("*** START OF THE PROJECT GUTENBERG EBOOK")
                end_idx = data.find("*** END OF THE PROJECT GUTENBERG EBOOK")
                
                if start_idx != -1 and end_idx != -1:
                    text_content = data[start_idx:end_idx]
                else:
                    text_content = data

                # Remove newlines and extra spaces to make it a continuous stream for searching
                text_content = " ".join(text_content.split())
                
                # Repeat text if it's too short, or slice it if it's too long
                while len(text_content) < length:
                    text_content += " " + text_content
                
                return text_content[:length]

            except Exception as e:
                # Fallback to random generation if fetch fails
                print(f"Failed to fetch text: {e}")
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