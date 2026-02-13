"""Tests for the forward geodesic calculator.

Verifies the math against known values. We check a few different
bearings and distances to make sure the formula is implemented correctly.
"""
import unittest
import math
import sys
import os

# add project root to path so imports work when running tests directly
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from domain.coordinate_calculator import CoordinateCalculator


class TestCoordinateCalculator(unittest.TestCase):

    def setUp(self):
        self.calc = CoordinateCalculator()

    def test_due_north(self):
        """Moving due north should increase latitude and keep longitude same."""
        lat, lon = self.calc.calculate_destination(0.0, 0.0, 0.0, 111_320)
        # 111,320 m is roughly 1 degree of latitude
        self.assertAlmostEqual(lat, 1.0, delta=0.02)
        self.assertAlmostEqual(lon, 0.0, delta=0.001)

    def test_due_east_from_equator(self):
        """Due east from equator: latitude unchanged, longitude increases."""
        lat, lon = self.calc.calculate_destination(0.0, 0.0, 90.0, 111_320)
        self.assertAlmostEqual(lat, 0.0, delta=0.02)
        self.assertAlmostEqual(lon, 1.0, delta=0.02)

    def test_due_south(self):
        """Due south decreases latitude."""
        lat, lon = self.calc.calculate_destination(10.0, 20.0, 180.0, 111_320)
        self.assertAlmostEqual(lat, 9.0, delta=0.02)
        self.assertAlmostEqual(lon, 20.0, delta=0.01)

    def test_short_distance(self):
        """Very short distance should barely move the point."""
        lat, lon = self.calc.calculate_destination(37.7749, -122.4194, 45.0, 10)
        self.assertAlmostEqual(lat, 37.7749, delta=0.001)
        self.assertAlmostEqual(lon, -122.4194, delta=0.001)

    def test_known_point_london_to_paris(self):
        """London (51.5074, -0.1278) heading ~150° for ~340 km should land near Paris."""
        lat, lon = self.calc.calculate_destination(51.5074, -0.1278, 150.0, 340_000)
        # Paris is around 48.86, 2.35 — we won't be exact but should be in the ballpark
        self.assertAlmostEqual(lat, 48.86, delta=0.5)
        # longitude should move east (positive direction)
        self.assertTrue(lon > -0.1278)

    def test_zero_distance_raises(self):
        """Zero distance should raise ValueError."""
        with self.assertRaises(ValueError):
            self.calc.calculate_destination(0, 0, 0, 0)

    def test_negative_distance_raises(self):
        with self.assertRaises(ValueError):
            self.calc.calculate_destination(0, 0, 0, -100)

    def test_accuracy_estimation(self):
        """Accuracy should increase with distance and be non-negative."""
        acc = self.calc.estimate_accuracy(10.0, 1000.0, compass_error_deg=5.0)
        self.assertGreater(acc, 0)

        # farther away = worse accuracy
        acc_near = self.calc.estimate_accuracy(10.0, 100.0)
        acc_far = self.calc.estimate_accuracy(10.0, 10000.0)
        self.assertGreater(acc_far, acc_near)

    def test_full_circle_bearing(self):
        """Bearing 360 should be same as bearing 0 (due north)."""
        lat1, lon1 = self.calc.calculate_destination(45.0, 10.0, 0.0, 50000)
        lat2, lon2 = self.calc.calculate_destination(45.0, 10.0, 360.0, 50000)
        self.assertAlmostEqual(lat1, lat2, places=6)
        self.assertAlmostEqual(lon1, lon2, places=6)

    def test_opposite_bearings(self):
        """Going north then south same distance should return near the start."""
        lat1, lon1 = self.calc.calculate_destination(40.0, -74.0, 0.0, 5000)
        lat2, lon2 = self.calc.calculate_destination(lat1, lon1, 180.0, 5000)
        self.assertAlmostEqual(lat2, 40.0, delta=0.001)
        self.assertAlmostEqual(lon2, -74.0, delta=0.001)


if __name__ == "__main__":
    unittest.main()
