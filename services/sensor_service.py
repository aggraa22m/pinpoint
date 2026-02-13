"""Accelerometer and gyroscope service for orientation stabilization.

Provides smoothed pitch/roll/tilt readings. On desktop this is simulated.
We use these values mainly to warn the user if the phone is tilted too much
(pointing at the ground or sky instead of the horizon).
"""
import math
from kivy.event import EventDispatcher
from kivy.properties import NumericProperty, BooleanProperty
from kivy.clock import Clock
from kivy.utils import platform
from kivy.logger import Logger

from utils.math_utils import smooth_values


class SensorService(EventDispatcher):
    pitch = NumericProperty(0.0)    # degrees, 0 = horizontal
    roll = NumericProperty(0.0)
    tilt_ok = BooleanProperty(True)  # False if phone is tilted too much

    TILT_THRESHOLD = 30.0  # warn if tilted more than this

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._accel = None
        self._gyro = None
        self._poll_event = None
        self._pitch_hist = []
        self._roll_hist = []

    def start(self):
        if platform in ("android", "ios"):
            self._start_real_sensors()
        else:
            self._start_mock()

    def stop(self):
        if self._accel:
            try:
                self._accel.disable()
            except Exception:
                pass
        if self._gyro:
            try:
                self._gyro.disable()
            except Exception:
                pass
        if self._poll_event:
            self._poll_event.cancel()

    def _start_real_sensors(self):
        try:
            from plyer import accelerometer, gyroscope
            self._accel = accelerometer
            self._accel.enable()

            try:
                self._gyro = gyroscope
                self._gyro.enable()
            except Exception:
                # gyro is optional, some cheap devices don't have one
                Logger.warning("SensorService: gyroscope not available")
                self._gyro = None

            self._poll_event = Clock.schedule_interval(self._read_sensors, 1 / 10)
            Logger.info("SensorService: sensors started")
        except Exception as e:
            Logger.error(f"SensorService: failed - {e}")
            self._start_mock()

    def _read_sensors(self, dt):
        if not self._accel:
            return
        try:
            acc = self._accel.acceleration
            if acc and acc[0] is not None:
                ax, ay, az = acc
                # compute pitch and roll from accelerometer
                pitch = math.degrees(math.atan2(ax, math.sqrt(ay**2 + az**2)))
                roll = math.degrees(math.atan2(ay, math.sqrt(ax**2 + az**2)))

                self._pitch_hist.append(pitch)
                self._roll_hist.append(roll)

                # trim history
                if len(self._pitch_hist) > 30:
                    self._pitch_hist = self._pitch_hist[-20:]
                    self._roll_hist = self._roll_hist[-20:]

                self.pitch = smooth_values(self._pitch_hist, window=5)
                self.roll = smooth_values(self._roll_hist, window=5)
                self.tilt_ok = abs(self.pitch) < self.TILT_THRESHOLD
        except Exception:
            pass

    def _start_mock(self):
        """Simulate level phone on desktop."""
        Logger.info("SensorService: mock mode (desktop)")
        self.pitch = 0.0
        self.roll = 0.0
        self.tilt_ok = True

        import random
        def _tick(dt):
            self.pitch = random.uniform(-3.0, 3.0)
            self.roll = random.uniform(-2.0, 2.0)
            self.tilt_ok = True

        self._poll_event = Clock.schedule_interval(_tick, 0.5)
