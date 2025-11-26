# COSC 520: Course Project: String_Matching_Algorithms

A comprehensive Python implementation and performance analysis of three fundamental string matching algorithms: Z-Algorithm, Bitap Algorithm, and Finite Automata.

## 📋 Table of Contents

- [Overview](#overview)
- [Algorithms Implemented](#algorithms-implemented)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Usage](#usage)
- [Performance Analysis](#performance-analysis)
- [Algorithm Complexity](#algorithm-complexity)
- [Dependencies](#dependencies)
- [Contributing](#contributing)

## 🌟 Features

- **Three Classic Algorithms:** Implementations of Z-Algorithm, Bitap, and Finite Automata
- **Performance Analysis:** Comprehensive benchmarking and comparison tools
- **Interactive Web Interface:** User-friendly Flask application for testing algorithms
- **Visualization:** Auto-generated performance comparison graphs
- **Extensible Design:** Modular architecture with algorithm wrapper for easy integration
- **Test Suite:** Included tests for application validation

## 🔍 Overview

This project provides efficient implementations of classic string matching algorithms with comprehensive performance evaluation tools. It includes both sample data demonstrations and realistic dataset testing capabilities, making it suitable for educational purposes and practical performance comparisons.

## 🚀 Algorithms Implemented

### 1. **Z-Algorithm**
The Z-Algorithm is an efficient linear-time pattern matching algorithm that constructs a Z-array.

- **Best for:** General purpose, single or multiple searches
- **Preprocessing:** O(m)
- **Matching:** O(n)
- **Space Complexity:** O(m+n)
- **Advantage:** Optimal linear time complexity

### 2. **Bitap Algorithm (Shift-Or)**
A bit-parallel approximate string matching algorithm that uses bitwise operations.

- **Best for:** Short patterns (≤64 characters), approximate matching
- **Preprocessing:** O(m)
- **Matching:** O(n)
- **Space Complexity:** O(m)
- **Advantage:** Fastest with hardware-optimized bit operations

### 3. **Finite Automata**
A deterministic finite automaton (DFA) based approach for pattern matching.

- **Best for:** Multiple searches on the same text, small alphabets
- **Preprocessing:** O(m³×|Σ|)
- **Matching:** O(n)
- **Space Complexity:** O(m×|Σ|)
- **Note:** Where m = pattern length, n = text length, |Σ| = alphabet size

## 📂 Project Structure

```text
String_Matching_Algorithms/
│
├── Application/                  # Web Application Module
│   ├── static/                   # Frontend assets
│   │   ├── script.js             # Client-side logic for API calls & highlighting
│   │   └── style.css             # UI styling
│   ├── templates/                # HTML Templates
│   │   └── index.html            # Main search interface
│   ├── tests/                    # Application Tests
│   │   └── test_app.py           # Unit tests for Flask routes
│   └── app.py                    # Flask server entry point
│
├── data/                         # Dataset storage
│
├── src/                          # Core Logic
│   ├── algorithims/              # String Matching Algorithm Implementations
│   │   ├── bitap.py              # Bitap (Shift-Or) Algorithm
│   │   ├── finite_automata.py    # Finite Automata Algorithm
│   │   └── z.py                  # Z-Algorithm
│   ├── datasets/                 # Data Utilities
│   │   ├── data_loaders.py       # Functions to load text files
│   │   └── download_create_datasets.py # Script to fetch/generate data
│   ├── algo_wrapper.py           # Wrapper to standardize algorithm calls
│   └── performance_evaluator.py  # Class for timing and memory profiling
│
├── demo.py                       # CLI script for quick algorithm demos
├── evaluate.py                   # CLI script for full performance benchmarking
├── performance_comparison.png    # Chart showing benchmark results
├── requirements.txt              # Project dependencies
└── README.md                     # Project documentation
```

## 💻 Installation

1. **Clone the repository:**
```bash
git clone https://github.com/dina-adel/String_Matching_Algorithms.git
cd String_Matching_Algorithms
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

## 🎯 Usage

### Quick Demo

Run the demo script to see all algorithms in action with sample data:

```bash
python demo.py
```

This will execute all three algorithms on sample datasets and display basic performance metrics.

### Benchmarking

For comprehensive performance analysis with realistic datasets:

```bash
python evaluate.py
```

This script will:
- Execute all algorithms on various test cases
- Measure and compare performance metrics
- Generate performance comparison plots (saved as `performance_comparison.png`)
- Display detailed benchmark results

### Web Application

Run the interactive web application to test algorithms visually:

```bash
cd Application
python app.py
```

Then open your browser and navigate to `http://localhost:5000` to use the web interface for testing string matching algorithms.

### Using Individual Algorithms

```python
from src.algorithims.z import z_algorithm
from src.algorithims.bitap import bitap_algorithm
from src.algorithims.finite_automata import finite_automata_match

# Example usage
text = "AABAACAADAABAABA"
pattern = "AABA"

# Z-Algorithm
matches = z_algorithm(text, pattern)

# Bitap Algorithm
matches = bitap_algorithm(text, pattern)

# Finite Automata
matches = finite_automata_match(text, pattern)
```

### Using the Algorithm Wrapper

```python
from src.algo_wrapper import AlgorithmWrapper

wrapper = AlgorithmWrapper()
text = "AABAACAADAABAABA"
pattern = "AABA"

# Run all algorithms
results = wrapper.run_all(text, pattern)
```

## 📊 Performance Analysis

The `performance_evaluator.py` module provides comprehensive tools to:

- Measure execution time for each algorithm
- Compare memory usage
- Analyze performance across different text and pattern sizes
- Generate visualization plots for comparative analysis
- Test with various alphabet sizes and pattern complexities

### Key Metrics Evaluated:
- **Execution Time:** Average time taken for pattern matching
- **Scalability:** Performance with increasing text/pattern sizes
- **Best/Worst Case:** Performance under optimal and challenging conditions

## ⚙️ Algorithm Complexity

| Algorithm | Preprocessing | Matching | Space | Best Use Case |
|-----------|--------------|----------|-------|---------------|
| Z-Algorithm | O(m) | O(n) | O(m+n) | General purpose |
| Bitap | O(m) | O(n) | O(m) | Short patterns |
| Finite Automata | O(m³×\|Σ\|) | O(n) | O(m×\|Σ\|) | Multiple searches |

**Where:**
- m = pattern length
- n = text length
- |Σ| = alphabet size

## 📦 Dependencies

- Python 3.x
- Flask (for web application)
- NumPy
- Matplotlib (for visualization)
- Additional dependencies listed in `requirements.txt`

Install all dependencies with:
```bash
pip install -r requirements.txt
```

## 🧪 Testing

Run the application test suite:

```bash
cd Application/tests
python test_app.py
```


---

⭐ If you find this project helpful, please consider giving it a star on GitHub!
