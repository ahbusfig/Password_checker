"""
tests/test_analyzer.py — Tests unitarios para checker.analyzer
"""

import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from Checkers.analyzer import analyze, analyze_many, PasswordResult


class TestAnalyzeReturnsPasswordResult(unittest.TestCase):

    def test_returns_dataclass(self):
        result = analyze("TestPassword1!")
        self.assertIsInstance(result, PasswordResult)

    def test_fields_present(self):
        r = analyze("TestPassword1!")
        self.assertIsNotNone(r.password)
        self.assertIsNotNone(r.length)
        self.assertIsNotNone(r.entropy)
        self.assertIsNotNone(r.score)
        self.assertIsNotNone(r.level)
        self.assertIsInstance(r.checks, dict)
        self.assertIsInstance(r.issues, list)
        self.assertIsInstance(r.suggestions, list)

    def test_score_range(self):
        for pwd in ["a", "123456", "P@ssw0rd!2024Secure", "aaaa"]:
            r = analyze(pwd)
            self.assertGreaterEqual(r.score, 0)
            self.assertLessEqual(r.score, 100)


class TestCommonPasswords(unittest.TestCase):

    def test_common_password_scores_zero(self):
        r = analyze("123456")
        self.assertEqual(r.score, 0)

    def test_common_password_check_false(self):
        r = analyze("password")
        self.assertFalse(r.checks["not_common"])

    def test_leet_common_detected(self):
        # "p@ssw0rd" → leet → "password" (común)
        r = analyze("p@ssw0rd")
        self.assertFalse(r.checks["not_common"])

    def test_unique_password_not_common(self):
        r = analyze("Xk9#mQ2$vL7!nR4@")
        self.assertTrue(r.checks["not_common"])


class TestChecks(unittest.TestCase):

    def test_min_length_false(self):
        self.assertFalse(analyze("abc").checks["min_length"])

    def test_min_length_true(self):
        self.assertTrue(analyze("abcdefgh").checks["min_length"])

    def test_good_length_true(self):
        self.assertTrue(analyze("abcdefghijkl").checks["good_length"])

    def test_has_uppercase(self):
        self.assertTrue(analyze("Abc").checks["has_uppercase"])
        self.assertFalse(analyze("abc").checks["has_uppercase"])

    def test_has_digit(self):
        self.assertTrue(analyze("abc1").checks["has_digit"])
        self.assertFalse(analyze("abcd").checks["has_digit"])

    def test_has_symbol(self):
        self.assertTrue(analyze("abc!").checks["has_symbol"])
        self.assertFalse(analyze("abc1").checks["has_symbol"])

    def test_no_repeating(self):
        self.assertFalse(analyze("aaabbb").checks["no_repeating"])
        self.assertTrue(analyze("aabbcc").checks["no_repeating"])

    def test_no_sequential(self):
        self.assertFalse(analyze("abcdefgh").checks["no_sequential"])
        self.assertTrue(analyze("Xk9mQvLn").checks["no_sequential"])

    def test_no_keyboard_walk(self):
        self.assertFalse(analyze("qwerty123").checks["no_keyboard_walk"])
        self.assertTrue(analyze("Xk9mQvLn!").checks["no_keyboard_walk"])


class TestLevels(unittest.TestCase):

    def test_common_is_muy_debil(self):
        self.assertEqual(analyze("123456").level, "Muy débil")

    def test_strong_password_level(self):
        r = analyze("Ag7#mK!qR2$nL9@z")
        self.assertIn(r.level, ["Fuerte", "Muy fuerte"])

    def test_levels_are_valid(self):
        valid = {"Muy débil", "Débil", "Moderada", "Fuerte", "Muy fuerte"}
        for pwd in ["a", "abcdefgh", "Abcdefgh1!", "Ag7#mK!qR2$nL9@z"]:
            self.assertIn(analyze(pwd).level, valid)


class TestAnalyzeMany(unittest.TestCase):

    def test_returns_list(self):
        results = analyze_many(["abc", "123456", "StrongP@ss1!"])
        self.assertIsInstance(results, list)
        self.assertEqual(len(results), 3)

    def test_empty_list(self):
        self.assertEqual(analyze_many([]), [])

    def test_order_preserved(self):
        passwords = ["abc", "xyz", "123"]
        results   = analyze_many(passwords)
        for pwd, r in zip(passwords, results):
            self.assertEqual(r.password, pwd)


if __name__ == "__main__":
    unittest.main(verbosity=2)
