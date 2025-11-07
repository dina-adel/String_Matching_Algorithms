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

