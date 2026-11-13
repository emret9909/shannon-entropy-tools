"""Tests for shannon_entropy_tools.core."""

import math
import unittest

from shannon_entropy_tools import (
    shannon_entropy,
    normalized_entropy,
    is_likely_compressed,
)


class TestShannonEntropy(unittest.TestCase):
    def test_empty_string_is_zero(self):
        self.assertEqual(shannon_entropy(""), 0.0)

    def test_empty_bytes_is_zero(self):
        self.assertEqual(shannon_entropy(b""), 0.0)

    def test_single_symbol_is_zero(self):
        self.assertEqual(shannon_entropy("aaaaa"), 0.0)
        self.assertEqual(shannon_entropy(b"\x00\x00\x00"), 0.0)

    def test_two_equally_likely_symbols_is_one_bit(self):
        self.assertAlmostEqual(shannon_entropy("ab"), 1.0, places=12)
        self.assertAlmostEqual(shannon_entropy(b"\x00\xff"), 1.0, places=12)

    def test_four_equally_likely_symbols_is_two_bits(self):
        self.assertAlmostEqual(shannon_entropy("abcd"), 2.0, places=12)

    def test_skewed_distribution_is_less_than_max(self):
        # Three a's and one b: H = -(0.75 log2 0.75 + 0.25 log2 0.25)
        expected = -(0.75 * math.log2(0.75) + 0.25 * math.log2(0.25))
        self.assertAlmostEqual(shannon_entropy("aaab"), expected, places=12)

    def test_bytearray_matches_bytes(self):
        data = b"hello world"
        self.assertAlmostEqual(
            shannon_entropy(bytearray(data)), shannon_entropy(data), places=12
        )

    def test_unicode_code_points(self):
        # Two distinct code points, equally likely.
        self.assertAlmostEqual(shannon_entropy("\u00e9\u00e8"), 1.0, places=12)

    def test_type_error_on_unsupported_input(self):
        with self.assertRaises(TypeError):
            shannon_entropy(123)  # type: ignore[arg-type]


class TestNormalizedEntropy(unittest.TestCase):
    def test_empty_is_zero(self):
        self.assertEqual(normalized_entropy(""), 0.0)
        self.assertEqual(normalized_entropy(b""), 0.0)

    def test_single_symbol_is_zero(self):
        self.assertEqual(normalized_entropy("aaaa"), 0.0)

    def test_uniform_binary_is_one(self):
        self.assertAlmostEqual(normalized_entropy("ab"), 1.0, places=12)

    def test_all_256_bytes_uniform_is_one(self):
        data = bytes(range(256))
        self.assertAlmostEqual(normalized_entropy(data), 1.0, places=12)

    def test_skewed_is_below_one(self):
        value = normalized_entropy("aaab")
        self.assertGreater(value, 0.0)
        self.assertLess(value, 1.0)

    def test_type_error_on_unsupported_input(self):
        with self.assertRaises(TypeError):
            normalized_entropy(None)  # type: ignore[arg-type]


class TestIsLikelyCompressed(unittest.TestCase):
    def test_empty_is_not_compressed(self):
        self.assertFalse(is_likely_compressed(b""))

    def test_english_text_is_not_compressed(self):
        text = b"the quick brown fox jumps over the lazy dog" * 10
        self.assertFalse(is_likely_compressed(text))

    def test_uniform_bytes_are_compressed(self):
        data = bytes(range(256)) * 4
        self.assertTrue(is_likely_compressed(data))

    def test_threshold_is_respected(self):
        data = bytes(range(256))
        self.assertTrue(is_likely_compressed(data, threshold=0.99))
        self.assertFalse(is_likely_compressed(data, threshold=1.01))

    def test_string_input(self):
        self.assertFalse(is_likely_compressed("hello"))


if __name__ == "__main__":
    unittest.main()
