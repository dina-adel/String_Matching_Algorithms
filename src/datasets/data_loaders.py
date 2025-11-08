
# ==============================================================
# Helper functions to load the prepared datasets
# ==============================================================

import os
from pathlib import Path

# Demo and testing functions
def load_sample_dataset():
    """
    Load or generate sample dataset for testing.
    
    Output:
        Dict containing text samples and patterns
    """
    # Sample DNA sequence
    dna_text = "GATCGGAAGAGCACACGTCTGAACTCCAGTCACATCACGATCTCGTATGCCGTCTTCTGCTTGAAA" * 100
    
    # Sample text (first paragraph of a book)
    book_text = """It was the best of times, it was the worst of times, it was the age of 
    wisdom, it was the age of foolishness, it was the epoch of belief, it was the epoch of 
    incredulity, it was the season of Light, it was the season of Darkness, it was the 
    spring of hope, it was the winter of despair.""" * 50
    
    return {
        'dna': {
            'text': dna_text,
            'patterns': ['GATC', 'AAAA', 'GTCT', 'CGTATGCCGTCTTCTGCTTG']
        },
        'book': {
            'text': book_text,
            'patterns': ['times', 'was the', 'age', 'of foolishness']
        }
    }

def load_real_datasets(base_dir="data"):
    """
    Loads the real Gutenberg text and DNA datasets along with their pattern files.
    Returns a dictionary with structure similar to the previous sample loader.
    """
    base_path = Path(base_dir)
    patterns_path = base_path / "patterns"

    book_file = base_path / "gutenberg.txt"
    dna_file = base_path / "dna_sample.txt"
    book_patterns = patterns_path / "patterns_gutenberg_meaningful.txt"
    dna_patterns = patterns_path / "patterns_dna.txt"

    if not book_file.exists() or not dna_file.exists():
        raise FileNotFoundError(
            f"Dataset files not found in {base_path}. "
            "Please run download_create_datasets.py first."
        )

    data = {
        "book": {
            "text": book_file.read_text(encoding="utf-8", errors="ignore"),
            "patterns": [
                line.strip()
                for line in book_patterns.read_text(encoding="utf-8").splitlines()
                if line.strip()
            ],
        },
        "dna": {
            "text": dna_file.read_text(encoding="utf-8", errors="ignore"),
            "patterns": [
                line.strip()
                for line in dna_patterns.read_text(encoding="utf-8").splitlines()
                if line.strip()
            ],
        },
    }

    return data

