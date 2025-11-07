import time
from typing import List, Dict, Tuple
import matplotlib.pyplot as plt
import numpy as np

class ZAlgorithm:
    """
    Z-Algorithm for String Matching
    
    This class implements the Z-algorithm, which computes the Z-array for efficient
    pattern matching in linear time.
    """
    
    def __init__(self, pattern: str):
        """
        Initialize the Z-Algorithm matcher.
        
        Input:
            pattern (str): The pattern to search for
        Output:
            None
        """
        self.pattern = pattern
        self.m = len(pattern)
    
    def _compute_z_array(self, s: str) -> List[int]:
        """
        Compute the Z-array for a string.
        
        Input:
            s (str): Input string
        Output:
            List[int]: Z-array where Z[i] is the length of longest substring starting
                      from s[i] which is also a prefix of s
        Explanation:
            Uses a window [L, R] to avoid redundant comparisons, achieving O(n) time.
        """
        n = len(s)
        z = [0] * n
        z[0] = n  # Z[0] is the length of the string itself
        
        l, r = 0, 0  # Window [l, r] where s[l..r] matches prefix
        
        for i in range(1, n):
            if i > r:
                # Outside window, compute Z[i] by explicit comparison
                l, r = i, i
                while r < n and s[r - l] == s[r]:
                    r += 1
                z[i] = r - l
                r -= 1
            else:
                # Inside window, use previously computed Z values
                k = i - l  # Corresponding position in prefix
                
                if z[k] < r - i + 1:
                    # Z[k] doesn't extend to boundary
                    z[i] = z[k]
                else:
                    # Z[k] extends to or beyond boundary, need to check further
                    l = i
                    while r < n and s[r - l] == s[r]:
                        r += 1
                    z[i] = r - l
                    r -= 1
        
        return z
    
    def search(self, text: str) -> List[int]:
        """
        Search for pattern occurrences in text using Z-algorithm.
        
        Input:
            text (str): The text to search in
        Output:
            List[int]: List of starting indices where pattern is found
        Explanation:
            Concatenates pattern and text with separator, computes Z-array,
            and finds positions where Z[i] equals pattern length.
        """
        # Concatenate pattern and text with a separator
        concat = self.pattern + "$" + text
        n = len(concat)
        
        # Compute Z-array for concatenated string
        z = self._compute_z_array(concat)
        
        # Find matches: positions where Z[i] == m
        matches = []
        for i in range(self.m + 1, n):
            if z[i] == self.m:
                # Match found at position i - (m + 1) in original text
                matches.append(i - self.m - 1)
        
        return matches

