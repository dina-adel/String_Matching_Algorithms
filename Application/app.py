from flask import Flask, render_template, request, jsonify, Response
import sys
import os
import csv
import io

# Add parent directory to path to allow importing src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.datasets.data_loaders import load_sample_dataset, load_real_datasets
from src.algo_wrapper import AlgorithmWrapper

app = Flask(__name__)

# Store current dataset in memory
APP_STATE = {
    "current_text": "",
    "current_dataset_name": "sample_dna",
    "datasets": {},
    "last_results": [],
    "last_pattern": ""  # Store the actual pattern used
}

def init_datasets():
    """Initialize available datasets"""
    samples = load_sample_dataset()
    APP_STATE["datasets"]["sample_dna"] = samples["dna"]["text"]
    APP_STATE["datasets"]["sample_book"] = samples["book"]["text"]
    
    try:
        # Calculate absolute path to data directory (in root)
        base_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
        real_data = load_real_datasets(base_dir=base_dir)
        APP_STATE["datasets"]["real_dna"] = real_data["dna"]["text"]
        APP_STATE["datasets"]["real_book"] = real_data["book"]["text"]
    except Exception as e:
        print(f"Real datasets not found or error loading: {e}")
        print("Using samples only.")
    
    APP_STATE["current_text"] = APP_STATE["datasets"]["sample_dna"]

init_datasets()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/datasets', methods=['GET'])
def get_datasets():
    return jsonify({
        "datasets": list(APP_STATE["datasets"].keys()),
        "current": APP_STATE["current_dataset_name"]
    })

@app.route('/api/dataset', methods=['GET', 'POST'])
def handle_dataset():
    if request.method == 'GET':
        return jsonify({"text": APP_STATE["current_text"]})
    
    if request.method == 'POST':
        data = request.json
        dataset_name = data.get('name')
        if dataset_name in APP_STATE["datasets"]:
            APP_STATE["current_dataset_name"] = dataset_name
            APP_STATE["current_text"] = APP_STATE["datasets"][dataset_name]
            return jsonify({"success": True, "text": APP_STATE["current_text"][:1000] + "..." if len(APP_STATE["current_text"]) > 1000 else APP_STATE["current_text"]})
        else:
            return jsonify({"error": "Dataset not found"}), 404

@app.route('/api/upload', methods=['POST'])
def upload_dataset():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    if file:
        text = file.read().decode('utf-8', errors='ignore')
        name = f"custom_{file.filename}"
        APP_STATE["datasets"][name] = text
        APP_STATE["current_dataset_name"] = name
        APP_STATE["current_text"] = text
        return jsonify({"success": True, "name": name})

@app.route('/api/operation', methods=['POST'])
def run_operation():
    data = request.json
    op_type = data.get('type')
    algo = data.get('algorithm')
    pattern = data.get('pattern')
    insert_text = data.get('insert_text', '')
    case_sensitive = data.get('case_sensitive', False)
    
    if not pattern:
        return jsonify({"error": "Pattern is required"}), 400
        
    text = APP_STATE["current_text"]
    original_pattern = pattern
    
    # Store original pattern for highlighting
    APP_STATE["last_pattern"] = original_pattern
    
    # Convert to lowercase for case-insensitive search
    if not case_sensitive:
        text = text.lower()
        pattern = pattern.lower()
    
    results = []

    if algo == "All":
        algorithms = ["Finite Automata", "Z-Algorithm"]
        if len(pattern) <= 64:
            algorithms.append("Bitap")
            
        for a in algorithms:
            res = AlgorithmWrapper.run_operation(op_type, a, text, pattern, insert_text)
            if "error" not in res:
                # Add the original pattern for display
                res["original_pattern"] = original_pattern
                res["case_sensitive"] = case_sensitive
                results.append(res)
    else:
        res = AlgorithmWrapper.run_operation(op_type, algo, text, pattern, insert_text)
        if "error" in res:
            return jsonify(res), 400
        res["original_pattern"] = original_pattern
        res["case_sensitive"] = case_sensitive
        results.append(res)
    
    # Update state if text modified
    if op_type in ['insert', 'delete'] and results:
        APP_STATE["current_text"] = results[0]["updated_text"]
        
    APP_STATE["last_results"] = results
    return jsonify(results if algo == "All" else results[0])

@app.route('/api/bulk_search', methods=['POST'])
def bulk_search():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    algo = request.form.get('algorithm', 'Finite Automata')
    case_sensitive = request.form.get('case_sensitive', 'false').lower() == 'true'
    
    if file:
        content = file.read().decode('utf-8', errors='ignore')
        patterns = [line.strip() for line in content.splitlines() if line.strip()]
        
        text = APP_STATE["current_text"]
        if not case_sensitive:
            text = text.lower()
            patterns = [p.lower() for p in patterns]
        
        result = AlgorithmWrapper.run_bulk_search(algo, text, patterns)
        return jsonify(result)
    return jsonify({"error": "Upload failed"}), 400

@app.route('/api/trace', methods=['POST'])
def trace_algo():
    data = request.json
    algo = data.get('algorithm')
    pattern = data.get('pattern')
    case_sensitive = data.get('case_sensitive', False)
    text = APP_STATE["current_text"]
    
    # Automatically limit to 500 characters for visualization
    max_trace_length = 250
    original_text = text
    
    if len(text) > max_trace_length:
        text = text[:max_trace_length]
        truncated = True
    else:
        truncated = False
    
    original_pattern = pattern
    
    # Convert to lowercase for case-insensitive
    if not case_sensitive:
        text = text.lower()
        pattern = pattern.lower()
        
    result = AlgorithmWrapper.run_trace(algo, text, pattern)
    
    # Add metadata for frontend
    if "error" not in result:
        result["original_pattern"] = original_pattern
        result["case_sensitive"] = case_sensitive
        result["original_text"] = original_text[:max_trace_length]
        result["truncated"] = truncated
        result["original_length"] = len(original_text)
    
    return jsonify(result)

@app.route('/api/generate', methods=['POST'])
def generate_dataset():
    data = request.json
    type = data.get('type')
    length = int(data.get('length'))
    
    try:
        text = AlgorithmWrapper.generate_text(type, length)
        name = f"generated_{type}_{length}"
        APP_STATE["datasets"][name] = text
        APP_STATE["current_dataset_name"] = name
        APP_STATE["current_text"] = text
        return jsonify({"success": True, "name": name, "text": text[:1000] + "..." if len(text) > 1000 else text})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/api/benchmark', methods=['POST'])
def benchmark():
    data = request.json
    algo = data.get('algorithm')
    pattern = data.get('pattern')
    max_length = int(data.get('max_length', 100000))
    step = int(data.get('step', 10000))
    
    if not pattern:
        return jsonify({"error": "Pattern is required"}), 400
        
    results = []
    
    if algo == "All":
        algorithms = ["Finite Automata", "Z-Algorithm"]
        if len(pattern) <= 64:
            algorithms.append("Bitap")
            
        for a in algorithms:
            res = AlgorithmWrapper.run_benchmark(a, pattern, max_length, step)
            if "error" not in res:
                results.append(res)
    else:
        res = AlgorithmWrapper.run_benchmark(algo, pattern, max_length, step)
        if "error" in res:
            return jsonify(res), 400
        results.append(res)
        
    return jsonify(results)

@app.route('/api/export', methods=['GET'])
def export_results():
    if not APP_STATE["last_results"]:
        return jsonify({"error": "No results to export"}), 400
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write headers
    writer.writerow(['Algorithm', 'Matches', 'Time (ms)', 'Space (KB)'])
    
    # Write data
    for result in APP_STATE["last_results"]:
        writer.writerow([
            result.get('algorithm', 'N/A'),
            result.get('match_count', 0),
            round(result.get('time_taken', 0) * 1000, 4),
            round(result.get('space_peak', 0) / 1024, 2)
        ])
    
    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=results.csv'}
    )

if __name__ == '__main__':
    app.run(debug=True)