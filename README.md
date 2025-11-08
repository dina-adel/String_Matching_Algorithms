# COSC 520: Course Project: String_Matching_Algorithms

### 1. Installation

```bash
# Install dependencies
pip install -r requirements.txt
```

### 2. Run the Demo or the Evaluation script

```bash
python demo.py
python evaluate.py
```

This will execute all algorithms on sample datasets and generate performance comparison plots.

---

## Project Structure

```
├── src

    ├── algorithms                              # algorithms implementation
        ├── z.py
        ├── bitap.py
        ├── finite_automata.py

    ├── datasets                                # dataset generation and sampling
        ├── data_loaders.py                     # loading both sample and realistic data
        ├── download_create_datasets.py         # downloading datasets & creating relevant patterns

    ├── performance_evaluator.py                # A class to handle algorithms evaluation

├── demo.py                                     # A demo run file using sample data
├── evaluate.py                                 # Evaluation script with real data
├── requirements.txt                            # Python dependencies
└── README.md                                   # This file
```

---

## Algorithm Descriptions

### Finite Automata (FA)
- **Best for:** Multiple searches on same text, small alphabets
- **Preprocessing:** O(m³×|Σ|)
- **Matching:** O(n)
- **Space:** O(m×|Σ|)

### Z-Algorithm
- **Best for:** General purpose, single or multiple searches
- **Preprocessing:** O(m)
- **Matching:** O(n)
- **Space:** O(m+n)
- **Optimal:** Linear time complexity

### Bitap (Shift-Or)
- **Best for:** Short patterns (≤64 chars), approximate matching
- **Preprocessing:** O(m)
- **Matching:** O(n)
- **Space:** O(m)
- **Fastest:** Hardware-optimized bit operations

---

**Last Updated:** November 2025