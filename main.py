"""
PinPoint — GPS coordinate projection app.

Points your phone at a distant object, enter the estimated distance,
and get the GPS coordinates of that object. Uses compass heading +
GPS position + forward geodesic math.

Run with:  python main.py
"""
import os
import sys

# make sure our project root is on the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from kivy.config import Config
# set window size for desktop testing — ignored on mobile
Config.set("graphics", "width", "400")
Config.set("graphics", "height", "750")
Config.set("graphics", "resizable", "0")

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, SlideTransition
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.logger import Logger

from domain.coordinate_calculator import CoordinateCalculator
from services.location_service import LocationService
from services.compass_service import CompassService
from services.sensor_service import SensorService
from data.location_repository import LocationRepository
from utils.permissions import request_app_permissions
from presentation.theme import Colors


class PinPointApp(App):

    def build(self):
        self.title = "PinPoint"
        Window.clearcolor = Colors.BG_PRIMARY

        # init services
        self.calculator = CoordinateCalculator()
        self.location_svc = LocationService()
        self.compass_svc = CompassService()
        self.sensor_svc = SensorService()
        self.repo = LocationRepository()

        # this gets set by camera screen when user hits "locate"
        self.last_result = None

        # screen manager with slide transitions
        self.sm = ScreenManager(transition=SlideTransition(duration=0.25))

        # screens are imported here to avoid circular deps
        from presentation.screens.camera_screen import CameraScreen
        from presentation.screens.result_screen import ResultScreen
        from presentation.screens.history_screen import HistoryScreen

        self.sm.add_widget(CameraScreen(app_ref=self))
        self.sm.add_widget(ResultScreen(app_ref=self))
        self.sm.add_widget(HistoryScreen(app_ref=self))

        # request permissions then start sensors
        request_app_permissions(callback=self._on_permissions)

        # start sensors after a short delay to let UI initialize
        Clock.schedule_once(self._start_services, 1.0)

        return self.sm

    def _on_permissions(self, permissions, grant_results):
        Logger.info(f"Permissions: {permissions} -> {grant_results}")

    def _start_services(self, dt):
        Logger.info("App: starting sensor services")
        self.location_svc.start()
        self.compass_svc.start()
        self.sensor_svc.start()

    def on_pause(self):
        # called when app goes to background on mobile
        return True

    def on_resume(self):
        # restart sensors when coming back
        self.location_svc.start()
        self.compass_svc.start()
        self.sensor_svc.start()

    def on_stop(self):
        self.location_svc.stop()
        self.compass_svc.stop()
        self.sensor_svc.stop()


if __name__ == "__main__":
    PinPointApp().run()
