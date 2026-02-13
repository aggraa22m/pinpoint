"""Local storage for saved locations.

Uses a simple JSON file. Nothing fancy — SQLite would be overkill for
what's basically a list of coordinates with timestamps.
"""
import json
import os
import logging
from datetime import datetime

# use stdlib logging so this module works without kivy installed (for tests)
try:
    from kivy.logger import Logger
except ImportError:
    Logger = logging.getLogger(__name__)


STORAGE_FILE = "saved_locations.json"


class SavedLocation:
    """Represents one saved result."""

    def __init__(self, src_lat, src_lon, dest_lat, dest_lon,
                 bearing, distance, accuracy, timestamp=None, label=""):
        self.src_lat = src_lat
        self.src_lon = src_lon
        self.dest_lat = dest_lat
        self.dest_lon = dest_lon
        self.bearing = bearing
        self.distance = distance
        self.accuracy = accuracy
        self.timestamp = timestamp or datetime.now().isoformat()
        self.label = label

    def to_dict(self):
        return {
            "src_lat": self.src_lat,
            "src_lon": self.src_lon,
            "dest_lat": self.dest_lat,
            "dest_lon": self.dest_lon,
            "bearing": self.bearing,
            "distance": self.distance,
            "accuracy": self.accuracy,
            "timestamp": self.timestamp,
            "label": self.label,
        }

    @classmethod
    def from_dict(cls, d):
        return cls(
            src_lat=d["src_lat"],
            src_lon=d["src_lon"],
            dest_lat=d["dest_lat"],
            dest_lon=d["dest_lon"],
            bearing=d["bearing"],
            distance=d["distance"],
            accuracy=d["accuracy"],
            timestamp=d.get("timestamp", ""),
            label=d.get("label", ""),
        )


class LocationRepository:
    def __init__(self, storage_dir=None):
        if storage_dir:
            self._path = os.path.join(storage_dir, STORAGE_FILE)
        else:
            # use app's user_data_dir at runtime
            from kivy.app import App
            app = App.get_running_app()
            if app:
                self._path = os.path.join(app.user_data_dir, STORAGE_FILE)
            else:
                self._path = STORAGE_FILE

        self._locations = []
        self._load()

    def _load(self):
        if os.path.exists(self._path):
            try:
                with open(self._path, "r") as f:
                    data = json.load(f)
                self._locations = [SavedLocation.from_dict(d) for d in data]
                Logger.info(f"LocationRepo: loaded {len(self._locations)} locations")
            except (json.JSONDecodeError, KeyError) as e:
                Logger.warning(f"LocationRepo: corrupted data, starting fresh - {e}")
                self._locations = []
        else:
            self._locations = []

    def _save(self):
        try:
            os.makedirs(os.path.dirname(self._path) or ".", exist_ok=True)
            with open(self._path, "w") as f:
                json.dump([loc.to_dict() for loc in self._locations], f, indent=2)
        except IOError as e:
            Logger.error(f"LocationRepo: save failed - {e}")

    def add(self, location):
        self._locations.insert(0, location)  # newest first
        self._save()

    def get_all(self):
        return list(self._locations)

    def delete(self, index):
        if 0 <= index < len(self._locations):
            self._locations.pop(index)
            self._save()

    def clear(self):
        self._locations.clear()
        self._save()

    @property
    def count(self):
        return len(self._locations)
