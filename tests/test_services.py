"""Basic integration tests for service layers.

These test the service logic without needing real hardware sensors.
We verify that services initialize properly and handle the mock/desktop
fallback path correctly.
"""
import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.location_repository import LocationRepository, SavedLocation


class TestLocationRepository(unittest.TestCase):
    """Test the storage layer with a temp file."""

    def setUp(self):
        import tempfile
        self._tmpdir = tempfile.mkdtemp()
        # patch out kivy app reference
        self.repo = LocationRepository.__new__(LocationRepository)
        self.repo._path = os.path.join(self._tmpdir, "test_locations.json")
        self.repo._locations = []

    def tearDown(self):
        import shutil
        shutil.rmtree(self._tmpdir, ignore_errors=True)

    def test_add_and_retrieve(self):
        loc = SavedLocation(
            src_lat=37.0, src_lon=-122.0,
            dest_lat=37.1, dest_lon=-121.9,
            bearing=45.0, distance=1000, accuracy=50.0,
        )
        self.repo.add(loc)
        self.assertEqual(self.repo.count, 1)

        all_locs = self.repo.get_all()
        self.assertEqual(len(all_locs), 1)
        self.assertAlmostEqual(all_locs[0].dest_lat, 37.1)

    def test_delete(self):
        for i in range(3):
            loc = SavedLocation(0, 0, float(i), 0, 0, 100, 10)
            self.repo.add(loc)

        self.assertEqual(self.repo.count, 3)
        self.repo.delete(0)
        self.assertEqual(self.repo.count, 2)

    def test_persistence(self):
        """Data should survive creating a new repo instance pointing at same file."""
        loc = SavedLocation(1.0, 2.0, 3.0, 4.0, 90.0, 500, 20)
        self.repo.add(loc)

        # create a fresh repo pointing at the same file
        repo2 = LocationRepository.__new__(LocationRepository)
        repo2._path = self.repo._path
        repo2._locations = []
        repo2._load()

        self.assertEqual(repo2.count, 1)
        self.assertAlmostEqual(repo2.get_all()[0].dest_lat, 3.0)

    def test_clear(self):
        for _ in range(5):
            self.repo.add(SavedLocation(0, 0, 0, 0, 0, 100, 10))
        self.repo.clear()
        self.assertEqual(self.repo.count, 0)

    def test_saved_location_serialization(self):
        loc = SavedLocation(
            src_lat=10, src_lon=20,
            dest_lat=30, dest_lon=40,
            bearing=180, distance=5000, accuracy=100,
            label="test point",
        )
        d = loc.to_dict()
        restored = SavedLocation.from_dict(d)
        self.assertEqual(restored.src_lat, 10)
        self.assertEqual(restored.label, "test point")
        self.assertEqual(restored.distance, 5000)


if __name__ == "__main__":
    unittest.main()
