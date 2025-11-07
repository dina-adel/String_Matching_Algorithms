import time
from typing import List, Dict, Tuple
import matplotlib.pyplot as plt
import numpy as np


class FiniteAutomataMatching:
    """
    Finite Automata-Based String Matching Algorithm
    
    This class implements pattern matching using a deterministic finite automaton (DFA).
    The DFA is constructed based on the pattern, and then used to scan the text once.
    """
    
    def __init__(self, pattern: str, alphabet: str = None):
        """
        Initialize the Finite Automata matcher.
        
        Input:
            pattern (str): The pattern to search for
            alphabet (str): The alphabet of characters to consider. If None, derives from pattern.
        Output:
            None
        """
        self.pattern = pattern
        self.m = len(pattern)
        
        # Determine alphabet from pattern if not provided
        if alphabet is None:
            self.alphabet = ''.join(sorted(set(pattern)))
        else:
            self.alphabet = alphabet
        
        # Build the transition table
        self.transition_table = self._build_transition_table()
    
    def _compute_lps(self, pattern: str, state: int, char: str) -> int:
        """
        Compute the longest prefix suffix for transition function.
        
        Input:
            pattern (str): The pattern being matched
            state (int): Current state
            char (str): Character to process
        Output:
            int: Next state number
        Explanation:
            Determines the next state by finding the longest prefix that is also a suffix.
        """
        # If character matches, move to next state
        if state < self.m and char == pattern[state]:
            return state + 1
        
        # Otherwise, find the longest proper prefix which is also suffix
        next_state = 0
        for ns in range(state, 0, -1):
            if pattern[ns - 1] == char:
                # Check if pattern[0..ns-2] matches pattern[state-ns+1..state-1]
                match = True
                for i in range(ns - 1):
                    if pattern[i] != pattern[state - ns + 1 + i]:
                        match = False
                        break
                if match:
                    next_state = ns
                    break
        
        return next_state
    
    def _build_transition_table(self) -> Dict[Tuple[int, str], int]:
        """
        Build the DFA transition table.
        
        Input:
            None (uses self.pattern and self.alphabet)
        Output:
            Dict[Tuple[int, str], int]: Transition table mapping (state, char) -> next_state
        Explanation:
            Constructs a DFA where each state represents a prefix match of the pattern.
        """
        transition_table = {}
        
        # For each state (0 to m, where m is pattern length)
        for state in range(self.m + 1):
            # For each character in alphabet
            for char in self.alphabet:
                next_state = self._compute_lps(self.pattern, state, char)
                transition_table[(state, char)] = next_state
        
        return transition_table
    
    def search(self, text: str) -> List[int]:
        """
        Search for pattern occurrences in text using FA.
        
        Input:
            text (str): The text to search in
        Output:
            List[int]: List of starting indices where pattern is found
        Explanation:
            Runs the DFA on the text, recording positions where final state is reached.
        """
        n = len(text)
        matches = []
        state = 0
        
        # Process each character in text
        for i in range(n):
            char = text[i]
            # Get next state from transition table
            if (state, char) in self.transition_table:
                state = self.transition_table[(state, char)]
            else:
                # Character not in alphabet, reset to state 0
                state = 0
            
            # If we reached the final state, pattern is found
            if state == self.m:
                matches.append(i - self.m + 1)
        
        return matches
