"""
Dataset preparation script for COSC 520 String Matching Project
Downloads real-world text (Gutenberg) and DNA sequence (Ensembl),
then generates meaningful patterns for benchmarking string matching algorithms.
All outputs are stored under the /data/ folder.
"""

import os
import re
import random
import gzip
import requests
from pathlib import Path


# ==============================================================
# Setup base directory
# ==============================================================
BASE_DIR = Path(__file__).resolve().parents[2] / "data"
BASE_DIR.mkdir(parents=True, exist_ok=True)
PATTERN_DIR = BASE_DIR / "patterns"
PATTERN_DIR.mkdir(exist_ok=True)


# ==============================================================
# 1. Download Gutenberg Text (English Literature)
# ==============================================================
def download_gutenberg(book_id=1342):
    """
    Downloads 'Pride and Prejudice' from Project Gutenberg.
    """
    out_path = BASE_DIR / "gutenberg.txt"
    if out_path.exists():
        print("✅ Gutenberg text already exists.")
        return out_path

    print("Downloading Gutenberg text...")
    url = f"https://www.gutenberg.org/files/{book_id}/{book_id}-0.txt"
    r = requests.get(url)
    if r.status_code != 200:
        raise RuntimeError(f"Failed to download Gutenberg book (HTTP {r.status_code})")
    out_path.write_text(r.text, encoding="utf-8")
    print(f"✅ Downloaded and saved → {out_path}")
    return out_path


# ==============================================================
# 2. Download Real DNA Sequence (Human Chromosome 1)
# ==============================================================
def download_dna_sample():
    """
    Downloads a real human DNA sequence from Ensembl (Chromosome 1)
    and extracts the first ~10MB for testing.
    """
    gz_path = BASE_DIR / "dna_chr1.fa.gz"
    out_path = BASE_DIR / "dna_sample.txt"

    if out_path.exists():
        print("✅ DNA sample already exists.")
        return out_path

    print("Downloading DNA sample (~50 MB)...")
    url = "https://ftp.ensembl.org/pub/release-112/fasta/homo_sapiens/dna/Homo_sapiens.GRCh38.dna.chromosome.1.fa.gz"
    r = requests.get(url, stream=True)
    if r.status_code != 200:
        raise RuntimeError(f"Failed to download DNA FASTA file (HTTP {r.status_code})")

    with open(gz_path, "wb") as f:
        for chunk in r.iter_content(chunk_size=8192):
            f.write(chunk)

    print("Extracting 10 MB DNA segment...")
    seq = []
    with gzip.open(gz_path, "rt") as fin:
        for line in fin:
            if not line.startswith(">"):
                seq.append(line.strip())
                if sum(len(s) for s in seq) > 10_000_000:
                    break

    dna_seq = "".join(seq)[:10_000_000]
    out_path.write_text(dna_seq)
    print(f"✅ Saved DNA sample text (~10 MB) → {out_path}")
    return out_path


# ==============================================================
# 3. Generate Meaningful Text Patterns (Words & Phrases)
# ==============================================================
def generate_meaningful_text_patterns(text_file, n=15, max_len=5):
    """
    Extracts realistic word-based patterns from the given text file.
    Example outputs: "Elizabeth Bennet", "Mr Darcy", "Netherfield Park"
    """
    text = Path(text_file).read_text(encoding="utf-8", errors="ignore")
    words = re.findall(r"[A-Za-z]+", text)
    if len(words) < 50:
        raise ValueError("Text file seems too small or malformed for pattern generation.")

    patterns = []
    for _ in range(n):
        start_idx = random.randint(0, len(words) - max_len)
        length = random.randint(1, max_len)
        phrase = " ".join(words[start_idx:start_idx + length])
        patterns.append(phrase.strip())

    out_path = PATTERN_DIR / "patterns_gutenberg_meaningful.txt"
    out_path.write_text("\n".join(patterns), encoding="utf-8")
    print(f"✅ Saved {n} meaningful text patterns → {out_path}")
    return out_path


# ==============================================================
# 4. Generate DNA Patterns (Known Motifs + Random Samples)
# ==============================================================
def generate_dna_patterns(dna_file, random_n=5, random_len=10):
    """
    Creates a mix of biological motifs and random DNA substrings.
    """
    dna_text = Path(dna_file).read_text(encoding="utf-8", errors="ignore")

    known_motifs = [
        "ATG",      # start codon
        "TATAAA",   # TATA box promoter
        "GGGCGG",   # GC box
        "AATAAA",   # polyadenylation signal
        "TTGACA",   # promoter element
        "AGGAGG"    # Shine-Dalgarno sequence
    ]

    random_patterns = []
    for _ in range(random_n):
        start = random.randint(0, len(dna_text) - random_len - 1)
        random_patterns.append(dna_text[start:start + random_len])

    all_patterns = known_motifs + random_patterns
    out_path = PATTERN_DIR / "patterns_dna.txt"
    out_path.write_text("\n".join(all_patterns), encoding="utf-8")
    print(f"✅ Saved DNA patterns (motifs + random) → {out_path}")
    return out_path


# ==============================================================
# 5. Main Runner
# ==============================================================
if __name__ == "__main__":
    print(f"📁 All data will be stored under: {BASE_DIR}")

    # Step 1: Download datasets
    gutenberg_path = download_gutenberg()
    dna_path = download_dna_sample()

    # Step 2: Generate patterns
    generate_meaningful_text_patterns(gutenberg_path)
    generate_dna_patterns(dna_path)

    print("\n🎯 Dataset preparation complete!")
    print("Data folder structure:")
    print(f" ├── {BASE_DIR / 'gutenberg.txt'}")
    print(f" ├── {BASE_DIR / 'dna_sample.txt'}")
    print(f" └── {PATTERN_DIR}/")
