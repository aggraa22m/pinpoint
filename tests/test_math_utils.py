"""Tests for math utility functions."""
import unittest
import math
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.math_utils import (
    deg_to_rad, rad_to_deg, normalize_heading,
    heading_to_cardinal, smooth_values, smooth_heading,
)


class TestConversions(unittest.TestCase):

    def test_deg_to_rad(self):
        self.assertAlmostEqual(deg_to_rad(0), 0.0)
        self.assertAlmostEqual(deg_to_rad(180), math.pi)
        self.assertAlmostEqual(deg_to_rad(90), math.pi / 2)
        self.assertAlmostEqual(deg_to_rad(360), 2 * math.pi)

    def test_rad_to_deg(self):
        self.assertAlmostEqual(rad_to_deg(0), 0.0)
        self.assertAlmostEqual(rad_to_deg(math.pi), 180.0)
        self.assertAlmostEqual(rad_to_deg(2 * math.pi), 360.0)

    def test_roundtrip(self):
        for deg in [0, 45, 90, 135, 180, 270, 359.5]:
            self.assertAlmostEqual(rad_to_deg(deg_to_rad(deg)), deg)


class TestHeading(unittest.TestCase):

    def test_normalize_positive(self):
        self.assertAlmostEqual(normalize_heading(0), 0.0)
        self.assertAlmostEqual(normalize_heading(359.9), 359.9)
        self.assertAlmostEqual(normalize_heading(360), 0.0)
        self.assertAlmostEqual(normalize_heading(720), 0.0)
        self.assertAlmostEqual(normalize_heading(450), 90.0)

    def test_normalize_negative(self):
        self.assertAlmostEqual(normalize_heading(-90), 270.0)
        self.assertAlmostEqual(normalize_heading(-180), 180.0)

    def test_cardinal_directions(self):
        self.assertEqual(heading_to_cardinal(0), "N")
        self.assertEqual(heading_to_cardinal(90), "E")
        self.assertEqual(heading_to_cardinal(180), "S")
        self.assertEqual(heading_to_cardinal(270), "W")
        self.assertEqual(heading_to_cardinal(45), "NE")
        self.assertEqual(heading_to_cardinal(135), "SE")
        self.assertEqual(heading_to_cardinal(225), "SW")
        self.assertEqual(heading_to_cardinal(315), "NW")


class TestSmoothing(unittest.TestCase):

    def test_smooth_values_empty(self):
        self.assertEqual(smooth_values([]), 0.0)

    def test_smooth_values_single(self):
        self.assertEqual(smooth_values([42.0]), 42.0)

    def test_smooth_values_constant(self):
        # constant values should smooth to the same value
        self.assertAlmostEqual(smooth_values([5.0, 5.0, 5.0, 5.0]), 5.0)

    def test_smooth_values_average(self):
        self.assertAlmostEqual(smooth_values([10, 20, 30], window=3), 20.0)

    def test_smooth_heading_no_wraparound(self):
        # normal case, no 0/360 boundary
        headings = [90, 91, 89, 90, 92]
        result = smooth_heading(headings, window=5)
        self.assertAlmostEqual(result, 90.4, delta=1.0)

    def test_smooth_heading_wraparound(self):
        # this is the tricky case: headings near 0/360 boundary
        headings = [358, 359, 0, 1, 2]
        result = smooth_heading(headings, window=5)
        # should be close to 0, not something weird like 180
        self.assertTrue(result < 10 or result > 350)

    def test_smooth_heading_empty(self):
        self.assertEqual(smooth_heading([]), 0.0)


if __name__ == "__main__":
    unittest.main()
