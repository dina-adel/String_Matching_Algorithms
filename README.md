# COSC 520: Course Project: String_Matching_Algorithms

### 1. Installation

```bash
# Install dependencies
pip install -r requirements.txt
```

### 2. Run the Demo

```bash
python demo.py
```

This will execute all algorithms on sample datasets and generate performance comparison plots.

---

## Project Structure

```
string-matching-project/
├── src
    ├── algorithms
        ├── z.py
        ├── bitap.py
        ├── finite_automata.py
    ├── datasets.py             # Handle dataset generation and sampling
    ├── performance_evaluator.py    # A class to handle algorithms evaluation
├── demo.py                     # A demo run file
├── requirements.txt            # Python dependencies
└── README.md                   # This file
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