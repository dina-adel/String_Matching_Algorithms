import time
from typing import List, Dict, Tuple
import matplotlib.pyplot as plt
import numpy as np

class BitapAlgorithm:
    """
    Bitap (Shift-Or) Algorithm for String Matching
    
    This class implements the Bitap algorithm, which uses bitwise operations
    for efficient approximate string matching. This implementation handles exact matching.
    """
    
    def __init__(self, pattern: str):
        """
        Initialize the Bitap algorithm matcher.
        
        Input:
            pattern (str): The pattern to search for (max 64 characters for standard int)
        Output:
            None
        """
        self.pattern = pattern
        self.m = len(pattern)
        
        if self.m > 64:
            raise ValueError("Pattern length exceeds 64 characters (integer bit limit)")
        
        # Build pattern mask for each character
        self.pattern_mask = self._build_pattern_mask()
    
    def _build_pattern_mask(self) -> dict[str, int]:
        """
        Build bit masks for each character in the pattern.
        
        Input:
            None (uses self.pattern)
        Output:
            Dict[str, int]: Mapping of character to its bit mask
        Explanation:
            For each character, sets bits at positions where character appears in pattern.
        """
        mask = {}
        
        # Initialize all masks to all 1s (using m bits)
        default_mask = (1 << self.m) - 1
        
        # For each position in pattern, set bit for that character
        for i, char in enumerate(self.pattern):
            if char not in mask:
                mask[char] = default_mask
            # Clear bit at position i (0-indexed from right)
            mask[char] &= ~(1 << i)
        
        return mask
    
    def search(self, text: str) -> List[int]:
        """
        Search for pattern occurrences in text using Bitap algorithm.
        
        Input:
            text (str): The text to search in
        Output:
            List[int]: List of starting indices where pattern is found
        Explanation:
            Uses bit-parallel approach with shift and OR operations to track
            potential matches as text is scanned.
        """
        n = len(text)
        matches = []
        
        # Initialize state: all 1s means no match yet
        state = (1 << self.m) - 1
        
        # Bit mask to check if pattern matched (1 at position m-1)
        match_mask = 1 << (self.m - 1)
        
        for i in range(n):
            char = text[i]
            
            # Get pattern mask for current character (default to all 1s)
            pattern_mask = self.pattern_mask.get(char, (1 << self.m) - 1)
            
            # Update state: shift left and OR with pattern mask
            state = ((state << 1) | pattern_mask)
            
            # Check if match found (bit at position m-1 is 0)
            if (state & match_mask) == 0:
                matches.append(i - self.m + 1)
        
        return matches
