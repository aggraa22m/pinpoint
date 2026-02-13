"""Compass / heading service.

Uses plyer compass on mobile, simulates on desktop.
Heading values are smoothed using circular averaging to reduce jitter.
"""
from kivy.event import EventDispatcher
from kivy.properties import NumericProperty, StringProperty, BooleanProperty
from kivy.clock import Clock
from kivy.utils import platform
from kivy.logger import Logger

from utils.math_utils import smooth_heading, heading_to_cardinal, normalize_heading


class CompassService(EventDispatcher):
    heading = NumericProperty(0.0)         # smoothed heading 0-360
    raw_heading = NumericProperty(0.0)     # unfiltered reading
    cardinal = StringProperty("N")
    is_active = BooleanProperty(False)
    needs_calibration = BooleanProperty(False)

    SMOOTHING_WINDOW = 8  # number of recent readings to average

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._heading_history = []
        self._compass = None
        self._poll_event = None

    def start(self):
        if self.is_active:
            return

        if platform in ("android", "ios"):
            self._start_real_compass()
        else:
            self._start_mock_compass()

    def stop(self):
        if self._compass:
            try:
                self._compass.disable()
            except Exception:
                pass

        if self._poll_event:
            self._poll_event.cancel()
            self._poll_event = None

        self._heading_history.clear()
        self.is_active = False

    def _start_real_compass(self):
        try:
            from plyer import compass
            self._compass = compass
            self._compass.enable()
            # poll the compass at ~15 Hz
            self._poll_event = Clock.schedule_interval(self._read_compass, 1 / 15)
            self.is_active = True
            Logger.info("CompassService: real compass enabled")
        except Exception as e:
            Logger.error(f"CompassService: compass failed - {e}")
            self._start_mock_compass()

    def _read_compass(self, dt):
        if not self._compass:
            return
        try:
            field = self._compass.field
            if field and field[0] is not None:
                import math
                # plyer gives (x, y, z) magnetic field — compute heading from x,y
                x, y = field[0], field[1]
                raw = math.degrees(math.atan2(y, x))
                raw = normalize_heading(-raw)  # flip sign convention
                self._update_heading(raw)
        except Exception as e:
            Logger.warning(f"CompassService: read error - {e}")
            self.needs_calibration = True

    def _start_mock_compass(self):
        """Simulate compass on desktop — slowly rotates for testing."""
        Logger.info("CompassService: mock compass mode")
        self.is_active = True
        self._mock_angle = 0.0

        import random
        def _tick(dt):
            # slow rotation with some noise, good enough for UI testing
            self._mock_angle = (self._mock_angle + 0.5) % 360
            noise = random.uniform(-2.0, 2.0)
            self._update_heading(self._mock_angle + noise)

        self._poll_event = Clock.schedule_interval(_tick, 1 / 15)

    def _update_heading(self, raw_deg):
        self.raw_heading = normalize_heading(raw_deg)
        self._heading_history.append(self.raw_heading)

        # don't let history grow forever
        if len(self._heading_history) > 50:
            self._heading_history = self._heading_history[-30:]

        self.heading = smooth_heading(self._heading_history, self.SMOOTHING_WINDOW)
        self.cardinal = heading_to_cardinal(self.heading)
