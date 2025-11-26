import json
from pathlib import Path

def merge_results():
    base_dir = Path("results")
    output_file = base_dir / "benchmark_results.json"
    
    all_results = []
    
    # Find all benchmark_results.json files in subdirectories
    for result_file in base_dir.rglob("benchmark_results.json"):
        if result_file == output_file:
            continue
            
        print(f"Found results file: {result_file}")
        try:
            with open(result_file, 'r') as f:
                data = json.load(f)
                if isinstance(data, list):
                    all_results.extend(data)
                    print(f"  Added {len(data)} records")
                else:
                    print(f"  Warning: Expected list in {result_file}, got {type(data)}")
        except Exception as e:
            print(f"  Error reading {result_file}: {e}")
            
    # Save merged results
    print(f"\nTotal records: {len(all_results)}")
    with open(output_file, 'w') as f:
        json.dump(all_results, f, indent=2)
    print(f"Merged results saved to: {output_file}")

if __name__ == "__main__":
    merge_results()
