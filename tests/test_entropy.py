"""
tests/test_entropy.py — Tests unitarios para checker.entropy
"""

import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from Checkers.entropy import calculate_entropy, detect_charset_size, entropy_label


class TestDetectCharsetSize(unittest.TestCase):

    def test_only_lowercase(self):
        self.assertEqual(detect_charset_size("abcdef"), 26)

    def test_only_uppercase(self):
        self.assertEqual(detect_charset_size("ABCDEF"), 26)

    def test_only_digits(self):
        self.assertEqual(detect_charset_size("123456"), 10)

    def test_lower_upper(self):
        self.assertEqual(detect_charset_size("abcABC"), 52)

    def test_lower_digits(self):
        self.assertEqual(detect_charset_size("abc123"), 36)

    def test_all_categories(self):
        self.assertEqual(detect_charset_size("aA1!"), 94)

    def test_empty(self):
        self.assertEqual(detect_charset_size(""), 0)

    def test_symbol_only(self):
        self.assertEqual(detect_charset_size("!@#$"), 32)

class TestCalculateEntropy(unittest.TestCase):

    def test_empty_password(self):
        self.assertEqual(calculate_entropy(""), 0.0)

    def test_entropy_increases_with_length(self):
        e1 = calculate_entropy("abc")
        e2 = calculate_entropy("abcdef")
        self.assertGreater(e2, e1)

    def test_entropy_increases_with_charset(self):
        e_lower  = calculate_entropy("aaaaaaaaaa")     # solo minúsculas
        e_mixed  = calculate_entropy("aA1!aA1!aA")     # todos los tipos
        self.assertGreater(e_mixed, e_lower)

    def test_known_value(self):
        # "a" × 8, charset=26 → 8 * log2(26) ≈ 37.6
        result = calculate_entropy("aaaaaaaa")
        self.assertAlmostEqual(result, 37.6, delta=0.2)

    def test_returns_float(self):
        self.assertIsInstance(calculate_entropy("test"), float)

class TestEntropyLabel(unittest.TestCase):

    def test_muy_baja(self):
        self.assertEqual(entropy_label(10), "Muy baja")

    def test_baja(self):
        self.assertEqual(entropy_label(30), "Baja")

    def test_aceptable(self):
        self.assertEqual(entropy_label(50), "Aceptable")

    def test_alta(self):
        self.assertEqual(entropy_label(70), "Alta")

    def test_muy_alta(self):
        self.assertEqual(entropy_label(90), "Muy alta")


if __name__ == "__main__":
    unittest.main(verbosity=2)
