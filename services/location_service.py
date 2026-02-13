"""GPS location service.

Wraps plyer's GPS or falls back to manual input on desktop.
On actual devices this gives real GPS readings. On desktop/emulator
it provides mock coordinates for testing.
"""
from kivy.event import EventDispatcher
from kivy.properties import NumericProperty, BooleanProperty
from kivy.clock import Clock
from kivy.utils import platform
from kivy.logger import Logger


class LocationService(EventDispatcher):
    latitude = NumericProperty(0.0)
    longitude = NumericProperty(0.0)
    accuracy = NumericProperty(0.0)
    is_active = BooleanProperty(False)
    is_mock = BooleanProperty(False)

    _gps = None
    _update_event = None

    def start(self):
        if self.is_active:
            return

        if platform in ("android", "ios"):
            self._start_real_gps()
        else:
            self._start_mock_gps()

    def stop(self):
        if not self.is_active:
            return

        if self._gps:
            try:
                self._gps.stop()
            except Exception as e:
                Logger.warning(f"LocationService: error stopping GPS - {e}")

        if self._update_event:
            self._update_event.cancel()
            self._update_event = None

        self.is_active = False
        Logger.info("LocationService: stopped")

    def _start_real_gps(self):
        try:
            from plyer import gps
            self._gps = gps
            self._gps.configure(
                on_location=self._on_location,
                on_status=self._on_status,
            )
            self._gps.start(minTime=1000, minDistance=1)
            self.is_active = True
            Logger.info("LocationService: real GPS started")
        except Exception as e:
            Logger.error(f"LocationService: failed to start GPS - {e}")
            # fall back to mock if real GPS fails
            self._start_mock_gps()

    def set_manual_location(self, lat, lon):
        """Let the user type in their own coordinates on desktop."""
        self.latitude = lat
        self.longitude = lon
        self.accuracy = 1.0
        self.is_active = True
        Logger.info(f"LocationService: manual location set to {lat}, {lon}")

    def _start_mock_gps(self):
        """Desktop fallback — no real GPS, user enters coords manually."""
        Logger.info("LocationService: mock GPS mode, waiting for manual input")
        self.latitude = 0.0
        self.longitude = 0.0
        self.accuracy = 0.0
        self.is_active = True
        self.is_mock = True

    def _on_location(self, **kwargs):
        self.latitude = kwargs.get("lat", self.latitude)
        self.longitude = kwargs.get("lon", self.longitude)
        self.accuracy = kwargs.get("accuracy", self.accuracy)

    def _on_status(self, stype, status):
        Logger.info(f"LocationService: status {stype} = {status}")
