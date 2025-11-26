"""
Scalable Dataset Generator for String Matching Algorithms
Generates realistic datasets at multiple scales with organized file structure
IMPROVED VERSION: Exactly 3 high-quality patterns per file
"""

import os
import random
import requests
from pathlib import Path
from typing import List, Tuple
import re


class DatasetGenerator:
    """Generate representative datasets at multiple scales for benchmarking."""
    
    DNA_BASES = ['A', 'T', 'G', 'C']
    SCALES = [100_000, 500_000, 1_000_000, 5_000_000, 10_000_000]
    
    def __init__(self, output_dir: str = "data/generated"):
        """Initialize generator with output directory."""
        self.output_dir = Path(output_dir)
        self.cache_dir = Path("data/cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Cache for real text sources
        self.real_text_cache = None
    
    def _download_real_english_corpus(self) -> str:
        """
        Download a large corpus of real English text.
        Uses multiple Project Gutenberg books to create diverse, natural text.
        """
        cache_file = self.cache_dir / "english_corpus.txt"
        
        if cache_file.exists():
            print("  Loading cached English corpus...")
            return cache_file.read_text(encoding='utf-8', errors='ignore')
        
        print("  Downloading real English text corpus (Project Gutenberg)...")
        
        # Multiple books for diversity
        book_ids = [
            1342,  # Pride and Prejudice
            11,    # Alice's Adventures in Wonderland
            1661,  # Sherlock Holmes
            84,    # Frankenstein
            98,    # A Tale of Two Cities
            2701,  # Moby Dick
            1952,  # The Yellow Wallpaper
            16,    # Peter Pan
            74,    # The Adventures of Tom Sawyer
            345,   # Dracula
        ]
        
        corpus = []
        
        for book_id in book_ids:
            try:
                url = f"https://www.gutenberg.org/files/{book_id}/{book_id}-0.txt"
                print(f"    Downloading book {book_id}...")
                response = requests.get(url, timeout=30)
                
                if response.status_code == 200:
                    text = response.text
                    
                    # Remove Project Gutenberg header/footer
                    start_markers = ["*** START OF", "***START OF"]
                    end_markers = ["*** END OF", "***END OF"]
                    
                    for marker in start_markers:
                        if marker in text:
                            text = text.split(marker, 1)[1]
                            break
                    
                    for marker in end_markers:
                        if marker in text:
                            text = text.split(marker, 1)[0]
                            break
                    
                    corpus.append(text)
                    print(f"    ✓ Downloaded {len(text):,} characters")
            
            except Exception as e:
                print(f"    ⚠️  Failed to download book {book_id}: {e}")
        
        if not corpus:
            raise RuntimeError("Failed to download any books!")
        
        full_corpus = "\n\n".join(corpus)
        
        # Cache it
        cache_file.write_text(full_corpus, encoding='utf-8')
        print(f"  ✓ Created corpus with {len(full_corpus):,} characters")
        
        return full_corpus
    
    def generate_realistic_english(self, length: int) -> str:
        """Generate realistic English text by sampling from real corpus."""
        if self.real_text_cache is None:
            self.real_text_cache = self._download_real_english_corpus()
        
        corpus = self.real_text_cache
        
        if length >= len(corpus):
            repetitions = (length // len(corpus)) + 1
            result = (corpus * repetitions)[:length]
        else:
            if length < len(corpus) // 2:
                start = random.randint(0, len(corpus) - length)
                result = corpus[start:start + length]
            else:
                result = []
                remaining = length
                while remaining > 0:
                    chunk_size = min(remaining, len(corpus) // 4)
                    start = random.randint(0, len(corpus) - chunk_size)
                    result.append(corpus[start:start + chunk_size])
                    remaining -= chunk_size
                result = "".join(result)[:length]
        
        return result
    
    def generate_random_dna(self, length: int) -> str:
        """Generate random DNA sequence with uniform distribution."""
        return ''.join(random.choices(self.DNA_BASES, k=length))
    
    def generate_realistic_dna(self, length: int) -> str:
        """Generate DNA with realistic characteristics."""
        gc_content = 0.42
        weights = [
            (1 - gc_content) / 2,  # A
            (1 - gc_content) / 2,  # T
            gc_content / 2,         # G
            gc_content / 2          # C
        ]
        
        sequence = []
        motifs = ['TATAAA', 'AGGAGG', 'GGGCGG', 'AATAAA', 'TTGACA', 'CAAT']
        
        i = 0
        while i < length:
            if random.random() < 0.05 and i < length - 10:
                motif = random.choice(motifs)
                sequence.append(motif)
                i += len(motif)
            elif random.random() < 0.10 and i < length - 20:
                repeat_unit = ''.join(random.choices(self.DNA_BASES, weights=weights, k=random.randint(2, 4)))
                repeat_count = random.randint(3, 8)
                sequence.append(repeat_unit * repeat_count)
                i += len(repeat_unit) * repeat_count
            else:
                sequence.append(random.choices(self.DNA_BASES, weights=weights)[0])
                i += 1
        
        return ''.join(sequence[:length])
    
    def generate_repetitive_text(self, length: int, pattern_len: int = 100) -> str:
        """Generate text with high repetition (worst case for some algorithms)."""
        pattern = 'A' * (pattern_len - 1) + 'B'
        repetitions = length // pattern_len + 1
        return (pattern * repetitions)[:length]
    
    def generate_three_patterns(self, text: str) -> List[Tuple[str, str, int]]:
        """
        Generate exactly 3 diverse, high-quality patterns from text.
        Returns: [(pattern, description, count), ...]
        
        Strategy:
        - Pattern 1: SHORT & COMMON (5-10 chars, frequent)
        - Pattern 2: MEDIUM (15-25 chars, moderate frequency)
        - Pattern 3: LONG (40-80 chars, may be rare)
        """
        patterns = []
        
        # Determine if text is English-like
        is_english = self._is_english_text(text)
        
        if is_english:
            patterns = self._generate_english_three_patterns(text)
        else:
            patterns = self._generate_sequence_three_patterns(text)
        
        # Ensure we have exactly 3 patterns
        if len(patterns) < 3:
            # Fallback: generate simple substring patterns
            patterns.extend(self._generate_fallback_patterns(text, 3 - len(patterns)))
        
        return patterns[:3]  # Ensure exactly 3
    
    def _is_english_text(self, text: str) -> bool:
        """Check if text appears to be English."""
        sample = text[:1000]
        return all(32 <= ord(c) <= 126 or c in '\n\r\t' for c in sample)
    
    def _generate_english_three_patterns(self, text: str) -> List[Tuple[str, str, int]]:
        """Generate 3 patterns for English text."""
        patterns = []
        
        # Extract words
        words = re.findall(r'\b\w+\b', text)
        if not words:
            return []
        
        # Count word frequencies
        word_counts = {}
        for word in words:
            if len(word) >= 3:
                word_lower = word.lower()
                word_counts[word_lower] = word_counts.get(word_lower, 0) + 1
        
        if not word_counts:
            return []
        
        sorted_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)
        
        # PATTERN 1: SHORT & COMMON (5-10 chars, high frequency)
        short_candidates = [(w, c) for w, c in sorted_words if 5 <= len(w) <= 10 and c >= 5]
        if short_candidates:
            word, count = short_candidates[0]
            patterns.append((word, f"short_common (len={len(word)})", count))
        
        # PATTERN 2: MEDIUM (15-25 chars, moderate frequency)
        # Try to find a phrase
        sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
        medium_found = False
        
        for _ in range(min(50, len(sentences))):
            sentence = random.choice(sentences)
            if len(sentence) >= 25:
                phrase = sentence[:random.randint(15, min(25, len(sentence)))].strip()
                if phrase and 15 <= len(phrase) <= 25:
                    count = text.count(phrase)
                    if count > 0:
                        patterns.append((phrase, f"medium_phrase (len={len(phrase)})", count))
                        medium_found = True
                        break
        
        # If no phrase found, use a medium-length word
        if not medium_found:
            medium_candidates = [(w, c) for w, c in sorted_words if 10 <= len(w) <= 20]
            if medium_candidates:
                word, count = medium_candidates[0]
                patterns.append((word, f"medium_word (len={len(word)})", count))
        
        # PATTERN 3: LONG (35-64 chars, MAX 64 for Bitap)
        long_found = False
        for _ in range(min(50, len(sentences))):
            sentence = random.choice(sentences)
            if len(sentence) >= 40:
                phrase = sentence[:random.randint(35, min(64, len(sentence)))].strip()
                if phrase and 35 <= len(phrase) <= 64:
                    count = text.count(phrase)
                    if count > 0:
                        patterns.append((phrase, f"long_phrase (len={len(phrase)})", count))
                        long_found = True
                        break
        
        # If no long phrase, create one from multiple words (but cap at 64)
        if not long_found and len(words) >= 10:
            num_words = random.randint(5, 10)
            start_idx = random.randint(0, len(words) - num_words)
            phrase = ' '.join(words[start_idx:start_idx + num_words])
            # Truncate to 64 if needed
            if len(phrase) > 64:
                phrase = phrase[:64].rsplit(' ', 1)[0]  # Cut at last word boundary
            count = text.count(phrase)
            if count > 0 and 35 <= len(phrase) <= 64:
                patterns.append((phrase, f"long_multiword (len={len(phrase)})", count))
        
        return patterns
    
    def _generate_sequence_three_patterns(self, text: str) -> List[Tuple[str, str, int]]:
        """Generate 3 patterns for DNA or other sequence data (MAX 64 chars)."""
        patterns = []
        text_len = len(text)
        
        # PATTERN 1: SHORT (6-10 chars, should be common)
        for _ in range(100):
            length = random.randint(6, 10)
            start = random.randint(0, text_len - length)
            pattern = text[start:start + length]
            count = text.count(pattern)
            if count >= 3:  # Ensure it's common enough
                patterns.append((pattern, f"short_sequence (len={length})", count))
                break
        
        # PATTERN 2: MEDIUM (15-25 chars)
        for _ in range(100):
            length = random.randint(15, 25)
            start = random.randint(0, text_len - length)
            pattern = text[start:start + length]
            count = text.count(pattern)
            if count >= 1:
                patterns.append((pattern, f"medium_sequence (len={length})", count))
                break
        
        # PATTERN 3: LONG (40-64 chars, MAX 64 for Bitap)
        for _ in range(100):
            length = random.randint(40, min(64, text_len // 10))
            start = random.randint(0, text_len - length)
            pattern = text[start:start + length]
            count = text.count(pattern)
            if count >= 1:
                patterns.append((pattern, f"long_sequence (len={length})", count))
                break
        
        return patterns
    
    def _generate_fallback_patterns(self, text: str, num_needed: int) -> List[Tuple[str, str, int]]:
        """Generate simple fallback patterns if other methods fail (MAX 64 chars)."""
        patterns = []
        text_len = len(text)
        
        lengths = [8, 20, 50][:num_needed]
        
        for length in lengths:
            if length >= text_len:
                length = max(3, text_len // 2)
            
            # Cap at 64 for Bitap compatibility
            length = min(length, 64)
            
            start = random.randint(0, text_len - length)
            pattern = text[start:start + length]
            count = text.count(pattern)
            patterns.append((pattern, f"fallback (len={length})", count))
        
        return patterns
    
    def generate_all_scales(self, dataset_type: str = "dna_realistic"):
        """
        Generate datasets at all scales for a given type.
        Each file gets exactly 3 patterns.
        """
        # Create organized subdirectory
        type_dir = self.output_dir / dataset_type
        type_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"\nGenerating {dataset_type} datasets...")
        print(f"Output directory: {type_dir}")
        
        for scale in self.SCALES:
            scale_label = self._format_scale(scale)
            print(f"  [{scale_label}] Generating {scale:,} characters...")
            
            # Generate text
            if dataset_type == "dna_random":
                text = self.generate_random_dna(scale)
            elif dataset_type == "dna_realistic":
                text = self.generate_realistic_dna(scale)
            elif dataset_type == "english":
                text = self.generate_realistic_english(scale)
            elif dataset_type == "repetitive":
                text = self.generate_repetitive_text(scale)
            else:
                raise ValueError(f"Unknown dataset type: {dataset_type}")
            
            # Save text file
            text_file = type_dir / f"text_{scale_label}.txt"
            text_file.write_text(text, encoding='utf-8')
            
            # Generate exactly 3 patterns
            patterns = self.generate_three_patterns(text)
            
            # Save patterns file
            patterns_file = type_dir / f"patterns_{scale_label}.txt"
            
            with open(patterns_file, 'w', encoding='utf-8') as f:
                f.write(f"# Three diverse patterns for {dataset_type} at scale {scale_label}\n")
                f.write(f"# All patterns are <= 64 characters (Bitap compatible)\n")
                f.write(f"# Format: pattern<TAB># description, occurs X times\n\n")
                
                for i, (pattern, description, count) in enumerate(patterns, 1):
                    # Escape special characters
                    pattern_escaped = pattern.replace('\t', '\\t').replace('\n', '\\n').replace('\r', '\\r')
                    f.write(f"{pattern_escaped}\t# Pattern {i}: {description}, occurs {count} times\n")
            
            print(f"      ✓ Saved text_{scale_label}.txt ({len(text):,} chars)")
            print(f"      ✓ Saved patterns_{scale_label}.txt (3 patterns)")
            
            # Show pattern details
            for i, (pattern, description, count) in enumerate(patterns, 1):
                preview = pattern[:30] + "..." if len(pattern) > 30 else pattern
                print(f"         Pattern {i}: {description}, occurs {count}x - '{preview}'")
    
    def _format_scale(self, scale: int) -> str:
        """Format scale into readable label (e.g., 1000 -> '1K')."""
        if scale >= 1_000_000:
            return f"{scale // 1_000_000}M"
        elif scale >= 1_000:
            return f"{scale // 1_000}K"
        else:
            return str(scale)
    
    def generate_benchmark_suite(self):
        """Generate complete benchmark suite with organized structure."""
        print("=" * 70)
        print("GENERATING COMPREHENSIVE BENCHMARK SUITE")
        print("=" * 70)
        print(f"Base directory: {self.output_dir}")
        print(f"Each dataset will have exactly 3 diverse patterns")
        print(f"All patterns limited to 64 characters (Bitap compatible)")
        print()
        
        dataset_types = [
            "english",
            "dna_realistic",
            "dna_random",
            "repetitive"
        ]
        
        for dtype in dataset_types:
            self.generate_all_scales(dtype)
         
        print("\n" + "=" * 70)
        print("DATASET GENERATION COMPLETE")
        print("=" * 70)
       

def main():
    """Main function to generate all datasets."""
    generator = DatasetGenerator()
    generator.generate_benchmark_suite()
    
    print("\n✅ All datasets generated successfully!")
    print("📊 Each pattern file contains exactly 3 diverse patterns:")
    print("   1. SHORT pattern (5-10 chars, common)")
    print("   2. MEDIUM pattern (15-25 chars, moderate)")
    print("   3. LONG pattern (35-64 chars, may be rare)")
    print("   ⚠️  All patterns are <= 64 chars for Bitap compatibility")

if __name__ == "__main__":
    main()