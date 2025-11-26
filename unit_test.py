import unittest
import sys
import os

# Add parent directory to path to import algorithms
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.algorithims.z import ZAlgorithm
from src.algorithims.bitap import BitapAlgorithm
from src.algorithims.finite_automata import FiniteAutomataMatching


class TestZAlgorithm(unittest.TestCase):
    """Test cases for Z-Algorithm implementation"""
    
    def test_simple_match(self):
        """Test basic pattern matching"""
        pattern = "AABA"
        text = "AABAACAADAABAABA"
        z_algo = ZAlgorithm(pattern)
        matches = z_algo.search(text)
        self.assertEqual(matches, [0, 9, 12])
    
    def test_no_match(self):
        """Test when pattern is not found"""
        pattern = "XYZ"
        text = "AABAACAADAABAABA"
        z_algo = ZAlgorithm(pattern)
        matches = z_algo.search(text)
        self.assertEqual(matches, [])
    
    def test_single_character_pattern(self):
        """Test single character pattern"""
        pattern = "A"
        text = "BANANA"
        z_algo = ZAlgorithm(pattern)
        matches = z_algo.search(text)
        self.assertEqual(matches, [1, 3, 5])
    
    def test_overlapping_matches(self):
        """Test overlapping pattern occurrences"""
        pattern = "AA"
        text = "AAAA"
        z_algo = ZAlgorithm(pattern)
        matches = z_algo.search(text)
        self.assertEqual(matches, [0, 1, 2])
    
    def test_pattern_equals_text(self):
        """Test when pattern equals the entire text"""
        pattern = "HELLO"
        text = "HELLO"
        z_algo = ZAlgorithm(pattern)
        matches = z_algo.search(text)
        self.assertEqual(matches, [0])
    
    def test_empty_text(self):
        """Test with empty text"""
        pattern = "ABC"
        text = ""
        z_algo = ZAlgorithm(pattern)
        matches = z_algo.search(text)
        self.assertEqual(matches, [])
    
    def test_pattern_longer_than_text(self):
        """Test when pattern is longer than text"""
        pattern = "ABCDEFGH"
        text = "ABC"
        z_algo = ZAlgorithm(pattern)
        matches = z_algo.search(text)
        self.assertEqual(matches, [])
    
    def test_numeric_pattern(self):
        """Test with numeric strings"""
        pattern = "123"
        text = "0123456123789123"
        z_algo = ZAlgorithm(pattern)
        matches = z_algo.search(text)
        self.assertEqual(matches, [1, 7, 13])


class TestBitapAlgorithm(unittest.TestCase):
    """Test cases for Bitap Algorithm implementation"""
    
    def test_simple_match(self):
        """Test basic pattern matching"""
        pattern = "AABA"
        bitap = BitapAlgorithm(pattern)
        text = "AABAACAADAABAABA"
        matches = bitap.search(text)
        self.assertEqual(matches, [0, 9, 12])
    
    def test_no_match(self):
        """Test when pattern is not found"""
        pattern = "XYZ"
        bitap = BitapAlgorithm(pattern)
        text = "AABAACAADAABAABA"
        matches = bitap.search(text)
        self.assertEqual(matches, [])
    
    def test_single_character_pattern(self):
        """Test single character pattern"""
        pattern = "A"
        bitap = BitapAlgorithm(pattern)
        text = "BANANA"
        matches = bitap.search(text)
        self.assertEqual(matches, [1, 3, 5])
    
    def test_overlapping_matches(self):
        """Test overlapping pattern occurrences"""
        pattern = "AA"
        bitap = BitapAlgorithm(pattern)
        text = "AAAA"
        matches = bitap.search(text)
        self.assertEqual(matches, [0, 1, 2])
    
    def test_pattern_equals_text(self):
        """Test when pattern equals the entire text"""
        pattern = "HELLO"
        bitap = BitapAlgorithm(pattern)
        text = "HELLO"
        matches = bitap.search(text)
        self.assertEqual(matches, [0])
    
    def test_empty_text(self):
        """Test with empty text"""
        pattern = "ABC"
        bitap = BitapAlgorithm(pattern)
        text = ""
        matches = bitap.search(text)
        self.assertEqual(matches, [])
    
    def test_pattern_longer_than_text(self):
        """Test when pattern is longer than text"""
        pattern = "ABCDEFGH"
        bitap = BitapAlgorithm(pattern)
        text = "ABC"
        matches = bitap.search(text)
        self.assertEqual(matches, [])
    
    def test_pattern_too_long(self):
        """Test that pattern over 64 chars raises error"""
        pattern = "A" * 65
        with self.assertRaises(ValueError):
            BitapAlgorithm(pattern)
    
    def test_max_length_pattern(self):
        """Test pattern at maximum length (64 chars)"""
        pattern = "A" * 64
        bitap = BitapAlgorithm(pattern)
        text = "B" * 100 + "A" * 64 + "C" * 50
        matches = bitap.search(text)
        self.assertEqual(matches, [100])
    
    def test_numeric_pattern(self):
        """Test with numeric strings"""
        pattern = "123"
        bitap = BitapAlgorithm(pattern)
        text = "0123456123789123"
        matches = bitap.search(text)
        self.assertEqual(matches, [1, 7, 13])


class TestFiniteAutomataMatching(unittest.TestCase):
    """Test cases for Finite Automata Algorithm implementation"""
    
    def test_simple_match(self):
        """Test basic pattern matching"""
        pattern = "AABA"
        fa = FiniteAutomataMatching(pattern)
        text = "AABAACAADAABAABA"
        matches = fa.search(text)
        self.assertEqual(matches, [0, 9, 12])
    
    def test_no_match(self):
        """Test when pattern is not found"""
        pattern = "XYZ"
        fa = FiniteAutomataMatching(pattern)
        text = "AABAACAADAABAABA"
        matches = fa.search(text)
        self.assertEqual(matches, [])
    
    def test_single_character_pattern(self):
        """Test single character pattern"""
        pattern = "A"
        fa = FiniteAutomataMatching(pattern)
        text = "BANANA"
        matches = fa.search(text)
        self.assertEqual(matches, [1, 3, 5])
    
    def test_overlapping_matches(self):
        """Test overlapping pattern occurrences"""
        pattern = "AA"
        fa = FiniteAutomataMatching(pattern)
        text = "AAAA"
        matches = fa.search(text)
        self.assertEqual(matches, [0, 1, 2])
    
    def test_pattern_equals_text(self):
        """Test when pattern equals the entire text"""
        pattern = "HELLO"
        fa = FiniteAutomataMatching(pattern)
        text = "HELLO"
        matches = fa.search(text)
        self.assertEqual(matches, [0])
    
    def test_empty_text(self):
        """Test with empty text"""
        pattern = "ABC"
        fa = FiniteAutomataMatching(pattern)
        text = ""
        matches = fa.search(text)
        self.assertEqual(matches, [])
    
    def test_pattern_longer_than_text(self):
        """Test when pattern is longer than text"""
        pattern = "ABCDEFGH"
        fa = FiniteAutomataMatching(pattern)
        text = "ABC"
        matches = fa.search(text)
        self.assertEqual(matches, [])
    
    def test_with_custom_alphabet(self):
        """Test with custom alphabet"""
        pattern = "AB"
        fa = FiniteAutomataMatching(pattern, alphabet="ABC")
        text = "ABABCAB"
        matches = fa.search(text)
        self.assertEqual(matches, [0, 2, 5])
    
    def test_character_not_in_alphabet(self):
        """Test with characters not in pattern alphabet"""
        pattern = "AB"
        fa = FiniteAutomataMatching(pattern)
        text = "AXBABCAB"
        matches = fa.search(text)
        # Should find matches where pattern appears with pattern's alphabet
        self.assertIn(3, matches)
        self.assertIn(6, matches)
    
    def test_numeric_pattern(self):
        """Test with numeric strings"""
        pattern = "123"
        fa = FiniteAutomataMatching(pattern)
        text = "0123456123789123"
        matches = fa.search(text)
        self.assertEqual(matches, [1, 7, 13])


class TestAlgorithmConsistency(unittest.TestCase):
    """Test that all algorithms produce consistent results"""
    
    def test_all_algorithms_agree(self):
        """Test that all three algorithms find the same matches"""
        test_cases = [
            ("AABA", "AABAACAADAABAABA"),
            ("ABC", "XYZABCDEFABCGHI"),
            ("AA", "AAAA"),
            ("123", "0123456123789123"),
            ("A", "BANANA"),
        ]
        
        for pattern, text in test_cases:
            z_algo = ZAlgorithm(pattern)
            bitap = BitapAlgorithm(pattern)
            fa = FiniteAutomataMatching(pattern)
            
            z_matches = z_algo.search(text)
            bitap_matches = bitap.search(text)
            fa_matches = fa.search(text)
            
            self.assertEqual(z_matches, bitap_matches, 
                           f"Z-Algorithm and Bitap disagree on pattern '{pattern}' in text '{text}'")
            self.assertEqual(z_matches, fa_matches, 
                           f"Z-Algorithm and FA disagree on pattern '{pattern}' in text '{text}'")
            self.assertEqual(bitap_matches, fa_matches, 
                           f"Bitap and FA disagree on pattern '{pattern}' in text '{text}'")


class TestEdgeCases(unittest.TestCase):
    """Test edge cases across all algorithms"""
    
    def test_repeated_pattern(self):
        """Test pattern that repeats itself"""
        pattern = "ABAB"
        text = "ABABABAB"
        
        z_algo = ZAlgorithm(pattern)
        bitap = BitapAlgorithm(pattern)
        fa = FiniteAutomataMatching(pattern)
        
        z_matches = z_algo.search(text)
        bitap_matches = bitap.search(text)
        fa_matches = fa.search(text)
        
        expected = [0, 2, 4]
        self.assertEqual(z_matches, expected)
        self.assertEqual(bitap_matches, expected)
        self.assertEqual(fa_matches, expected)
    
    def test_special_characters(self):
        """Test with special characters"""
        pattern = "a.b"
        text = "a.b c.d a.b"
        
        z_algo = ZAlgorithm(pattern)
        bitap = BitapAlgorithm(pattern)
        fa = FiniteAutomataMatching(pattern)
        
        z_matches = z_algo.search(text)
        bitap_matches = bitap.search(text)
        fa_matches = fa.search(text)
        
        expected = [0, 8]
        self.assertEqual(z_matches, expected)
        self.assertEqual(bitap_matches, expected)
        self.assertEqual(fa_matches, expected)
    
    def test_case_sensitivity(self):
        """Test that matching is case-sensitive"""
        pattern = "abc"
        text = "ABCabcABC"
        
        z_algo = ZAlgorithm(pattern)
        bitap = BitapAlgorithm(pattern)
        fa = FiniteAutomataMatching(pattern)
        
        z_matches = z_algo.search(text)
        bitap_matches = bitap.search(text)
        fa_matches = fa.search(text)
        
        expected = [3]
        self.assertEqual(z_matches, expected)
        self.assertEqual(bitap_matches, expected)
        self.assertEqual(fa_matches, expected)


def run_tests():
    """Run all test suites"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestZAlgorithm))
    suite.addTests(loader.loadTestsFromTestCase(TestBitapAlgorithm))
    suite.addTests(loader.loadTestsFromTestCase(TestFiniteAutomataMatching))
    suite.addTests(loader.loadTestsFromTestCase(TestAlgorithmConsistency))
    suite.addTests(loader.loadTestsFromTestCase(TestEdgeCases))
    
    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "="*70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("="*70)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)