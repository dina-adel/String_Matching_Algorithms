from flask import Flask, render_template, request, jsonify, Response
import os
import csv
import io
from src.datasets.data_loaders import load_sample_dataset, load_real_datasets
from src.algo_wrapper import AlgorithmWrapper

app = Flask(__name__)

# Store current dataset in memory
APP_STATE = {
    "current_text": "",
    "current_dataset_name": "sample_dna",
    "datasets": {},
    "last_results": [] # Store for export
}

def init_datasets():
    """Initialize available datasets"""
    samples = load_sample_dataset()
    APP_STATE["datasets"]["sample_dna"] = samples["dna"]["text"]
    APP_STATE["datasets"]["sample_book"] = samples["book"]["text"]
    
    try:
        real_data = load_real_datasets()
        APP_STATE["datasets"]["real_dna"] = real_data["dna"]["text"]
        APP_STATE["datasets"]["real_book"] = real_data["book"]["text"]
    except Exception:
        print("Real datasets not found, using samples only.")
    
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
    
    if not pattern:
        return jsonify({"error": "Pattern is required"}), 400
        
    text = APP_STATE["current_text"]
    results = []

    if algo == "All":
        algorithms = ["Finite Automata", "Z-Algorithm"]
        # Only add Bitap if pattern is short enough
        if len(pattern) <= 64:
            algorithms.append("Bitap")
            
        for a in algorithms:
            res = AlgorithmWrapper.run_operation(op_type, a, text, pattern, insert_text)
            if "error" not in res:
                results.append(res)
    else:
        res = AlgorithmWrapper.run_operation(op_type, algo, text, pattern, insert_text)
        if "error" in res:
            return jsonify(res), 400
        results.append(res)
    
    # Update state if text modified (only takes effect from the first successful run if multiple)
    # For "All", we probably shouldn't modify text in-place cumulatively, or just take the first one.
    # For simplicity, if "All" is selected with Insert/Delete, we'll just return the result of the first one
    # but not actually update the global state to avoid chaos, or just update it once.
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
    
    if file:
        content = file.read().decode('utf-8', errors='ignore')
        patterns = [line.strip() for line in content.splitlines() if line.strip()]
        
        result = AlgorithmWrapper.run_bulk_search(algo, APP_STATE["current_text"], patterns)
        return jsonify(result)
    return jsonify({"error": "Upload failed"}), 400

@app.route('/api/trace', methods=['POST'])
def trace_algo():
    data = request.json
    algo = data.get('algorithm')
    pattern = data.get('pattern')
    text = APP_STATE["current_text"]
    
    # Limit text for trace
    if len(text) > 100:
        text = text[:100]
        
    result = AlgorithmWrapper.run_trace(algo, text, pattern)
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

if __name__ == '__main__':
    app.run(debug=True)
